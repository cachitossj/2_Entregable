

# Data Engineering Final Project

 **Data Extraction Pipeline RIOT GAMES API**.

![enter image description here](https://mmos.com/wp-content/uploads/2020/01/riot-games-new-logo-red-bg-banner.jpg)
 
 # League of Legends
 
  ## Contexto
 ![enter image description here](https://nosnerds.com.br/wp-content/uploads/2018/01/background-1002091.jpg)

**League of Legends (LoL)** es un popular juego en línea de estrategia en tiempo real (MOBA) desarrollado por **Riot Games**. En este juego, los jugadores asumen el papel de "invocadores" que controlan a campeones con habilidades únicas. El objetivo es trabajar en equipo para destruir la base enemiga, conocida como el "nexo". Se enfrentan dos equipos, cada uno compuesto por cinco jugadores (5v5), y la victoria se logra al coordinar estrategias y habilidades para superar al equipo contrario.

Con una impresionante variedad de más de 162 campeones, cada uno con su estilo de juego único y habilidades distintivas, LoL ofrece una experiencia dinámica y estratégica.

 Este juego ha atraído a millones de jugadores en todo el mundo y ha consolidado su posición como uno de los títulos más influyentes en la escena de los deportes electrónicos.

## Motivación
   
Como jugador apasionado de LoL, siempre he sentido **curiosidad** por explorar más allá de las partidas individuales y sumergirme en los datos que rodean este vasto universo de estrategia y competición. 

Este proyecto se convierte en la **oportunidad perfecta** para fusionar mi interés en los videojuegos con el aprendizaje práctico de técnicas y herramientas de **ingeniería de datos**. A lo largo de este proceso, espero no solo adquirir habilidades valiosas en dicho campo, sino también obtener perspectivas profundas sobre el juego. 

Es el resultado de **horas de trabajo**, **dedicación** y **pasión**. ¡Bienvenidos a disfrutar de este proyecto tanto como yo disfruté creándolo!.

# Descripción del proyecto

Este proyecto consiste en la creación de un **Pipeline de extracción de datos** utilizando la API de Riot Games. (Agregar más detalles sobre lo que consiste).

# API de RIOT GAMES
![enter image description here](https://thedraftlab.files.wordpress.com/2016/07/riot-api-landing.png)

La [API de Riot Games](https://developer.riotgames.com/) proporciona acceso a datos relacionados con League of Legends (2009), permitiendo a los desarrolladores obtener información detallada sobre jugadores, partidas y otras estadísticas del juego. Algunas de las capacidades clave de la API incluyen:

-  **Obtención de Datos del Jugador**: Accede a información detallada sobre un jugador, incluyendo datos personales de la cuenta, estadísticas de partidas, clasificaciones, y más.

-  **Historial de Partidas**: Recupera el historial completo de partidas de un jugador, con detalles como duración, campeones seleccionados, y resultados.

-  **Detalles de Partidas**: Obtén información específica de cada partida, incluyendo tiempo de inicio, duración, equipos participantes, y más.

Para más información o detalles, se recomienda leer la siguiente [Documentación](https://developer.riotgames.com/docs/lol).

>Nota: RIOT GAMES es propietaria de más juegos como: Teamfight Tactics (2019), Legends of Runeterra (2020), Valorant (2020), entre otros. En este proyecto solo nos enfocaremos en League of Legends (2009).


## Enpoints utilizados
- **[LEAGUE-V4](https://developer.riotgames.com/apis#league-v4)**: Utilizado para obtener información de la cuenta del jugador. Especificamente, de la liga en la que se encuentra.

| Tipo de petición | URL                                  |
| ----------------- | ------------------------------------ |
| GET               | [/lol/league/v4/entries/by-summoner/{encryptedSummonerId}](https://developer.riotgames.com/apis#league-v4/GET_getLeagueEntriesForSummoner)  |

Return value: Set[LeagueEntryDTO]

| NAME           | DATA TYPE | DESCRIPTION                                       |
| -------------- | --------- | ------------------------------------------------- |
| leagueId       | string    |                                                   |
| summonerId     | string    | Player's encrypted summonerId.                    |
| summonerName   | string    |                                                   |
| queueType      | string    |                                                   |
| tier           | string    |                                                   |
| rank           | string    | The player's division within a tier.              |
| leaguePoints   | int       |                                                   |
| wins           | int       | Winning team on Summoners Rift.                   |
| losses         | int       | Losing team on Summoners Rift.                   |
 
 ---
 - **[MATCH-V5](https://developer.riotgames.com/apis#match-v5)**: Utilizado para obtener todo tipo de información relacionada sobre las partidas del jugador. Se utilizaron 2 Endpoints:
 
 
 | Tipo de petición | URL                                  |
| ----------------- | ------------------------------------ |
| GET               | [/lol/match/v5/matches/by-puuid/{puuid}/ids](https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID)|

Return value: List[string]

**QUERY PARAMETERS**:
| Parameter | Value       | Data Type | Description                                                                                                                   |
|-----------|-------------|-----------|-------------------------------------------------------------------------------------------------------------------------------|
| startTime (optional) | 1689771600  | long      | Epoch timestamp in seconds. The matchlist started storing timestamps on June 16th, 2021. Any matches played before June 16th, 2021 won't be included if the startTime filter is set. |
| endTime (optional)   |             | long      | Epoch timestamp in seconds.                                                                                                  |
| queue (optional)     | 420         | int       | Filter the list of match ids by a specific queue id. This filter is mutually inclusive of the type filter.                   |
| type (optional)      | ranked      | string    | Filter the list of match ids by the type of match. This filter is mutually inclusive of the queue filter.                    |
| start (optional)     | 0           | int       | Defaults to 0. Start index.                                                                                                   |
| count (optional)     | 100         | int       | Defaults to 20. Valid values: 0 to 100. Number of match ids to return.                                                       |
---
**Justificación de la elección de los parámetros**:

Se decidió filtrar las partidas del jugador mediante varios parámetros para obtener **resultados más personalizados**: 
- 'starTime'. La fecha en formato Epoch, indicaría:
**GMT/UTC**: miércoles, 19 de julio de 2023 13:00:00  
**En su tiempo**: miércoles, 19 de julio de 2023 10:00:00 GMT-03:00

La decisión de utilizar esa fecha se debe a que es el *Inicio de la Temporada Clasificatoria (Split 2)*.
[Conversor utilizado](https://espanol.epochconverter.com/).

- 'queue 'y 'type'. Estos parámetros nos ayudan a filtrar el tipo de partida:

 | queueId | description|
| ----------------- | ------------------------------------ |
| 420               | 5v5 Ranked Solo games|

[Documentación](https://developer.riotgames.com/docs/lol) [Apartado de "Working with LoL APIs", "Queue IDs"]
[JSON](https://static.developer.riotgames.com/docs/lol/queues.json)

---
 | Tipo de petición | URL                                  |
| ----------------- | ------------------------------------ |
| GET               | [/lol/match/v5/matches/{matchId}](https://developer.riotgames.com/apis#match-v5/GET_getMatch))|

Probablemente este **Endpoint** sea el más **Complejo** e **Importante** del proyecto, debido a la GRAN cantidad y VARIEDAD de datos que contiene. 

Con él, obtendremos información valiosa acerca de las **Estadísticas** de la partida, **Indicadores**, **Campeones** utilizados, **Items** y muchos más!

**¡Te invito a que investigues todo el contenido y estructura del JSON, con este [Ejemplo](https://jsonhero.io/j/qKeDJ6to4myy)!**

---
# REDSHIFT

## Creación de las tablas

   **dim_matches:** Contiene información "temporal" de la partida, como la duración en Minutos, fecha y horario de creación, etc.
   Se definió como **Clave de Ordenamiento** a **'gameId'**, ya que va a ser usada frecuentemente para realizar consultas de búsqueda.
   En cuanto al **Estilo de Distribución**, se optó por usar el tipo **KEY** ya que es útil cuando las consultas suelen involucrar unir tablas mediante esa clave.

     -- Tabla dim_matches
    
    CREATE TABLE
    leosmaretto_dev_coderhouse.dim_matches (
    
    gameId INTEGER PRIMARY KEY distkey,
    puuid VARCHAR(80) NOT NULL,
    gameCreation TIMESTAMP NOT NULL,
    gameStartTimestamp TIMESTAMP NOT NULL,
    gameEndTimestamp TIMESTAMP NOT NULL,
    team1_win BOOLEAN NOT NULL,
    team2_win BOOLEAN NOT NULL,
    gameDurationMinutes FLOAT NOT NULL
    )
    SORTKEY(gameId);
**fact_player_stats:** Contiene las Estadísticas y Métricas del jugador en la partida, como la cantidad de Kills, las Asistencias, Muertes, KDA, entre otros.
   Se definió como **Clave de Ordenamiento** a **'puuid' y  'gameId'**, ya que va a ser usada frecuentemente para realizar consultas de búsqueda.
   En cuanto al **Estilo de Distribución**, se optó por usar el tipo **KEY** ya que es útil cuando las consultas suelen involucrar unir tablas mediante esa clave. Fue asignada a **'gameId'**.
   

    -- Tabla fact_player_stats
    
    CREATE TABLE
    leosmaretto_dev_coderhouse.fact_player_stats (
    
    puuid VARCHAR(80) NOT NULL,
    summonerId VARCHAR(80) NOT NULL,
    gameId INTEGER NOT NULL distkey,
    teamId INTEGER NOT NULL,
    summonerName VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL,
    lane VARCHAR(30) NOT NULL,
    teamPosition VARCHAR(30) NOT NULL,
    individualPosition VARCHAR(30) NOT NULL,
    win BOOLEAN NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    kda FLOAT NOT NULL,
    killParticipation FLOAT NOT NULL,
    damagePerMinute FLOAT NOT NULL,
    totalDamageDealt INTEGER NOT NULL,
    totalMinionsKilled INTEGER NOT NULL,
    neutralMinionsKilled INTEGER NOT NULL,
    goldEarned INTEGER NOT NULL,
    goldSpent INTEGER NOT NULL,
    goldPerMinute FLOAT NOT NULL,
    PRIMARY KEY (puuid, gameId),
    FOREIGN KEY (gameId) REFERENCES 
    leosmaretto_dev_coderhouse.dim_matches(gameId)
    )
    SORTKEY(puuid, gameId);