# ---------------IMPORTACIÓN DE LIBRERÍAS---------------#
import requests
import logging
import json

from configparser import ConfigParser
from typing import List, Dict, Optional

import os
import platform

import pandas as pd

from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from contextlib import contextmanager
import psycopg2
# ------------------------------------------------------#
# ----------------CREDENCIALES UTILIZADAS---------------#
config = ConfigParser()
config.read("config/config.ini")
params = {
    # ----------API RIOTGAMES----------
    "base_url_region": config["api_riot"]["base_url_region"],
    "base_url_server": config["api_riot"]["base_url_server"],
    "API_KEY": config["api_riot"]["API_KEY"],
    # ----------Información del jugador----------
    "player_name": config["player_info"]["player_name"],
    "player_id": config["player_info"]["player_id"],
    "player_puuid": config["player_info"]["player_puuid"],
    "region": config["player_info"]["region"],
    "servidor": config["player_info"]["servidor"],
    # ----------Endpoints----------
    "SUMMONER-V4_byname": config["endpoint_url"]["SUMMONER-V4_byname"],
    "LEAGUE-V4_entries_by-summner": config["endpoint_url"]["LEAGUE-V4_entries_by-summner"],
    "MATCH-V5": config["endpoint_url"]["MATCH-V5"],
    "MATCHES-V5": config["endpoint_url"]["MATCHES-V5"],
    # ----------Query Parameters----------
    "startTime": config["query_parameters"]["startTime"],
    "queue": config["query_parameters"]["queue"],
    "type": config["query_parameters"]["type"],
    "start": config["query_parameters"]["start"],
    "count": config["query_parameters"]["count"],
    # ----------Redshift----------
    "host": config["redshift"]["host"],
    "port": config["redshift"]["port"],
    "username": config["redshift"]["username"],
    "pwd": config["redshift"]["pwd"],
    "dbname": config["redshift"]["dbname"]
}
# -----------------------------------------------------#

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------FUNCIONES DEFINIDAS---------------#

# Será utilizada para retornar una Lista con los IDs de todo el historial de partidas del jugador.


def get_full_matches_history(player_puuid: str, start_time: int, queue: int, match_type: str, batch_size: int = 100) -> List[str]:

    match_ids = []
    start = 0
    flag = True

    logging.info(f'Review of game history...')

    while flag:
        try:
            endpoint = f"{params['base_url_region']}/{params['MATCH-V5']}{player_puuid}/ids?startTime={start_time}&queue={queue}&type={match_type}&start={start}&count={batch_size}&api_key={params['API_KEY']}"
            response = requests.get(endpoint)

            if response.status_code == 200:
                batch_match_ids = response.json()
                # Verificamos si hay más partidas
                if not batch_match_ids:
                    logging.info(f'No more games were found.')
                    flag = False  # No hay más partidas, salimos del bucle.

                # Actualizamos la lista con nuestros ids de las partidas.
                match_ids += batch_match_ids
                start += batch_size
            else:
                logging.error(
                    f"Error: {response.status_code}, {response.content}")
                flag = False
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while making request: {e}")
            flag = False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            flag = False
    logging.info(f'THE GAME HISTORY WAS SUCCESSFULLY OBTAINED!')

    return match_ids

# Será utilizada para retornar un diccionario con toda la información de las partidas, en base a los IDs de ellas.


def get_match_info(match_id: str) -> Dict:
    endpoint = f'{params["base_url_region"]}/{params["MATCHES-V5"]}{match_id}?api_key={params["API_KEY"]}'
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            match_details = response.json()
            return match_details['info']
        else:
            logging.error(
                f'Failed to fetch details for match {match_id}. Status code: {response.status_code}, Error: {response.content}')
            return None
    except requests.exceptions.RequestException as e:
        logging.error(
            f'Error while fetching details for match {match_id}: {e}')
        return None
    except Exception as e:
        logging.error(
            f'Unexpected error while fetching details for match {match_id}: {e}')
        return None

# Será utilizada para retornar un DataFrame con información 'Temporal' de las partidas, filtradas para nuestro jugador de interés.


def extract_match_details(player_puuid: str, start_time: int, queue: str, match_type: str) -> pd.DataFrame:
    try:
        # Acá obtenemos el historial de partidas.
        full_match_history = get_full_matches_history(
            player_puuid, start_time, queue, match_type)

        match_details_list = []

        logging.info('Fetching details for matches...')

        for match_id in full_match_history:
            # Obtenemos los detalles de la partida.
            match_data = get_match_info(match_id)

            # Verificamos si la obtención de datos fue exitosa.
            if match_data:
                # filtramos el índice del jugador en la lista de participantes (10 jugadores x partida).
                index_player = next(
                    (index for index, participant in enumerate(
                        match_data['participants']) if participant['puuid'] == params['player_puuid']), None)

                # Verificamos si se encontró el índice.
                if index_player is not None:

                    # Procedemos a extraer la información deseada.
                    gameId = match_data['gameId']
                    puuid = match_data['participants'][index_player]['puuid']
                    gameCreation = match_data['gameCreation']
                    gameStartTimestamp = match_data['gameStartTimestamp']
                    gameEndTimestamp = match_data['gameEndTimestamp']
                    gameDuration = match_data['gameDuration']
                    team1_win = match_data['teams'][0]['win']
                    team2_win = match_data['teams'][1]['win']

                    match_details_list.append([gameId, puuid, gameCreation, gameStartTimestamp,
                                               gameEndTimestamp, gameDuration, team1_win, team2_win])
                else:
                    logging.warning(
                        f"Player with PUUID {params['player_puuid']} not found in match {match_id}")

        # Armamos el DataFrame con los datos obtenidos previamente.
        df_match_details = pd.DataFrame(match_details_list, columns=[
                                        'gameId', 'puuid', 'gameCreation', 'gameStartTimestamp', 'gameEndTimestamp',
                                        'gameDuration', 'team1_win', 'team2_win'])

        logging.info('Data retrieval successful!')

        return df_match_details

    except requests.exceptions.RequestException as e:
        logging.error(f'Error while making request: {e}')
        return pd.DataFrame()
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return pd.DataFrame()

# Será utilizada para retornar un Diccionario con el listado de Campeones actualizados en el juego, ya que filtramos por Versión.
def get_champion_data() -> Dict:
    try:
        # Obtenemos la lista de versiones.
        version_list = requests.get(
            'https://ddragon.leagueoflegends.com/api/versions.json').json()

        # Obtenemos datos de campeones para la última versión.
        response = requests.get(
            f'https://ddragon.leagueoflegends.com/cdn/{version_list[0]}/data/es_AR/champion.json')

        if response.status_code == 200:
            champion_data = response.json()
            logging.info('Champion data successfully obtained!')
            return champion_data
        else:
            logging.error(
                f'Failed to obtain champion data. Status code: {response.status_code}')
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f'Error while making request: {e}')
        return None
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return None

# Será utilizada para retornar un Dataframe con información de cada uno de los Campeones del juego.
def extract_champion_info(champion_data: Dict) -> pd.DataFrame:
    try:
        champions = champion_data['data'].keys()
        data = []

        for champ in champions:

            # Filtramos la información de interés.
            id = champion_data['data'][champ]['id']
            key = champion_data['data'][champ]['key']
            name = champion_data['data'][champ]['name']
            title = champion_data['data'][champ]['title']
            info = champion_data['data'][champ]['info']
            partype = champion_data['data'][champ]['partype']
            image_full = champion_data['data'][champ]['image']['full']
            image_sprite = champion_data['data'][champ]['image']['sprite']
            tags = champion_data['data'][champ]['tags']
            stats = champion_data['data'][champ]['stats']

            data.append([id, key, name, title, info, partype,
                         image_full, image_sprite, tags, stats])

        df = pd.DataFrame(data, columns=[
                          'id', 'key', 'name', 'title', 'info', 'partype', 'image_full', 'image_sprite', 'tags', 'stats'])

        df_info = pd.json_normalize(df['info'])
        df_stats = pd.json_normalize(df['stats'])

        champion_data_clean = pd.concat([df, df_info, df_stats], axis=1)
        champion_data_clean = champion_data_clean.drop(
            ['info', 'stats'], axis=1)

        logging.info('Champion info successfully extracted!')
        return champion_data_clean

    except Exception as e:
        logging.error(f'Error extracting champion info: {e}')
        return None

# Será utilizada para retornar un Diccionario con el listado de Items actualizados en el juego, ya que filtramos por Versión.
def get_items_data() -> Dict:
    try:
        # Obtenemos la lista de versiones.
        version_list = requests.get(
            'https://ddragon.leagueoflegends.com/api/versions.json').json()

        # Obtenemos datos de campeones para la última versión.
        response = requests.get(
            f'https://ddragon.leagueoflegends.com/cdn/{version_list[0]}/data/es_AR/item.json')

        if response.status_code == 200:
            items_data = response.json()
            logging.info('items data successfully obtained!')
            return items_data
        else:
            logging.error(
                f'Failed to obtain items data. Status code: {response.status_code}')
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f'Error while making request: {e}')
        return None
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return None

# Será utilizada para retornar un Dataframe con información de cada uno de los Items del juego.
def extract_items_info(items_data: Dict) -> pd.DataFrame:
    try:
        items = items_data['data'].keys()
        data = []

        for item_id in items:

            # Filtramos la información de interés.
            name = items_data['data'][item_id]['name']
            full = items_data['data'][item_id]['image']['full']
            sprite = items_data['data'][item_id]['image']['sprite']
            base = items_data['data'][item_id]['gold']['base']
            purchasable = items_data['data'][item_id]['gold']['purchasable']
            total = items_data['data'][item_id]['gold']['total']
            sell = items_data['data'][item_id]['gold']['sell']
            tags = items_data['data'][item_id]['tags']
            stats = items_data['data'][item_id]['stats']

            data.append([item_id, name, full,
                        sprite, base, purchasable, total, sell, tags, stats])

        df = pd.DataFrame(data, columns=['id', 'name', 'full', 'sprite', 'base',
                                         'purchasable', 'total', 'sell', 'tags', 'stats'])

        # ----------TRANSFORMACIONES----------

        # Realizamos la normalización de las columnas JSON.
        df_stats = pd.json_normalize(df['stats'])
        df_items_clean = pd.concat([df, df_stats], axis=1)

        # Eliminamos columnas para evitar duplicados
        df_items_clean = df_items_clean.drop(['stats'], axis=1)

        # Dado que no todos los itrms tienen las mismas estadísticas, rellenamos los valores NaN con 0.
        df_items_clean.iloc[:, 9:] = df_items_clean.iloc[:, 9:].fillna(0)

        logging.info('Items info successfully extracted!')
        return df_items_clean

    except Exception as e:
        logging.error(f'Error extracting items info: {e}')
        return None

# Será utilizada para retornar un diccionario con toda la información de las partidas (filtrada para nuestro jugador de interés), en base a los IDs de ellas.
def get_match_stats(match_id: str) -> Dict:
    endpoint = f'{params["base_url_region"]}/{params["MATCHES-V5"]}{match_id}?api_key={params["API_KEY"]}'
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            match_details = response.json()

            # Obtenemos el índice del jugador en las partidas, para filtrarlo entre todos los participantes.
            index_player = match_details['metadata']['participants'].index(
                params['player_puuid'])

            # Creamos un diccionario con la información del jugador y la información adicional
            result = {
                'player_info': match_details['info']['participants'][index_player],
                'gameId': match_details['info']['gameId']
            }
            return result
        else:
            logging.error(
                f'Failed to fetch details for match {match_id}. Status code: {response.status_code}, Error: {response.content}')
            return None
    except requests.exceptions.RequestException as e:
        logging.error(
            f'Error while fetching details for match {match_id}: {e}')
        return None
    except Exception as e:
        logging.error(
            f'Unexpected error while fetching details for match {match_id}: {e}')
        return None

# Será utilizada para retornar un DataFrame con información y métricas del jugador, dentro de la partida.
def extract_player_match_stats(player_puuid: str, start_time: int, queue: int, match_type: str) -> pd.DataFrame:

    # Lista para almacenar las estadísticas de las partidas.
    match_stats_list = []

    try:
        # Obtener los ids de todas las partidas
        match_ids = get_full_matches_history(
            player_puuid, start_time, queue, match_type)  # ACÁ SE GENERA EL LOGGING DUPLICADO NUEVAMENTE, POR LA LLAMADA A LA FUNCIÓN

        # Iteraramos sobre los ids de las partidas y obtenemos las estadísticas del jugador.
        for match_id in match_ids:
            match_stats = get_match_stats(match_id)

            # Verificamos si las estadísticas fueron obtenidas con éxito.
            if match_stats:
                # Filtramos solo la información que necesitamos.
                filtered_stats = {
                    'puuid': match_stats['player_info']['puuid'],
                    'summonerId': match_stats['player_info']['summonerId'],
                    'gameId': match_stats['gameId'],
                    'teamId': match_stats['player_info']['teamId'],
                    'summonerName': match_stats['player_info']['summonerName'],
                    'role': match_stats['player_info']['role'],
                    'lane': match_stats['player_info']['lane'],
                    'teamPosition': match_stats['player_info']['teamPosition'],
                    'individualPosition': match_stats['player_info']['individualPosition'],
                    'win': match_stats['player_info']['win'],
                    'kills': match_stats['player_info']['kills'],
                    'deaths': match_stats['player_info']['deaths'],
                    'kda': match_stats['player_info']['challenges'].get('kda', None),
                    'killParticipation': match_stats['player_info']['challenges'].get('killParticipation', None),
                    'damagePerMinute': match_stats['player_info']['challenges'].get('damagePerMinute', None),
                    'totalDamageDealt': match_stats['player_info']['totalDamageDealt'],
                    'totalMinionsKilled': match_stats['player_info']['totalMinionsKilled'],
                    'neutralMinionsKilled': match_stats['player_info']['neutralMinionsKilled'],
                    'goldEarned': match_stats['player_info']['goldEarned'],
                    'goldSpent': match_stats['player_info']['goldSpent'],
                    'goldPerMinute': match_stats['player_info']['challenges'].get('goldPerMinute', None),
                }

                # Agregamos las estadísticas filtradas a la lista.
                match_stats_list.append(filtered_stats)

        df_match_stats = pd.DataFrame(match_stats_list)

        logging.info('Data retrieval successful!')

        return df_match_stats

    except requests.exceptions.RequestException as e:
        logging.error(f'Error while making request: {e}')
        return pd.DataFrame()
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return pd.DataFrame()

# Será utilizada para hacer la conexión con la Base de Datos.
def connect_to_db(config_file: str, section: str):
    try:
        parser = ConfigParser()
        parser.read(config_file)

        database = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                database[param[0]] = param[1]

            logging.info(f'connecting to the database...')
            engine = create_engine(
                f"postgresql://{database['username']}:{database['pwd']}@{database['host']}:{database['port']}/{database['dbname']}?sslmode=require",
                connect_args={
                    "options": f"-c search_path={database['schema']}"}
            )

            logging.info('database connection established successfully.')
            return engine
        else:
            raise Exception(
                f'Section {section} not found in file {config_file}')
    except Exception as e:
        logging.error(
            f'Error connecting to database: {type(e).__name__} - {str(e)}')
        return None

@contextmanager
def db_connection(config_file: str, section: str):
    # Crea la conexión a la base de datos
    engine = connect_to_db(config_file, section)
    if engine is not None:
        try:
            yield engine
        finally:
            engine.dispose()

def load_to_sql(df: pd.DataFrame, table_name: str, engine: Engine, if_exist: str = 'replace') -> None:
    try:
        logging.info('loading data into the database...')
        df.to_sql(
            table_name,
            engine,
            if_exists=if_exist,
            method="multi",
            index=False
        )
        logging.info('data successfully loaded into the database.')
    except Exception as e:
        logging.error(f'Error loading data into database: {e}')

# -----------------------------------------------------#

try:
    df_match_details = extract_match_details(
        params["player_puuid"], params["startTime"], params["queue"], params["type"])

    # ----------TRANSFORMACIONES----------
    # Procedemos a cambiar el formato Epoch a DateTime.
    df_match_details['gameCreation'] = pd.to_datetime(
        df_match_details['gameCreation'], unit='ms')

    df_match_details['gameStartTimestamp'] = pd.to_datetime(
        df_match_details['gameStartTimestamp'], unit='ms')

    df_match_details['gameEndTimestamp'] = pd.to_datetime(
        df_match_details['gameEndTimestamp'], unit='ms')

    # Para expresar esta columna en Minutos, tendremos que restar las dos columnas, luego hacer una trasformación.
    df_match_details['gameDurationMinutes'] = (
        df_match_details['gameEndTimestamp'] - df_match_details['gameStartTimestamp']).astype('timedelta64[ms]') / (1000 * 60)

    # Redondeamos los resultados de las columnas para que se visualicen con 2 decimales.
    df_match_details['gameDurationMinutes'] = df_match_details['gameDurationMinutes'].round(
        2)

    df_match_details = df_match_details.drop(['gameDuration'], axis=1)

except Exception as e:
    logging.error(f'Error in processing: {e}')

df_matches = df_match_details

try:
    df_player_stats = extract_player_match_stats(
        params["player_puuid"], params["startTime"], params["queue"], params["type"])

    logging.info('Data retrieval successful!')
except Exception as e:
    logging.error(f'Error occurred: {e}')

# --------------------Stage--------------------

df_stage = pd.merge(df_matches, df_player_stats, on='gameId')
df_stage = df_stage.drop(columns='puuid_y')
df_stage = df_stage.rename(columns={'puuid_x': 'puuid'})

# --------------------Conexión a la base de datos--------------------

with db_connection('config/config.ini', 'redshift') as engine:
    load_to_sql(df_matches, 'dim_matches', engine)
    load_to_sql(df_player_stats, 'fact_player_stats', engine)
    load_to_sql(df_stage, 'stage', engine)
