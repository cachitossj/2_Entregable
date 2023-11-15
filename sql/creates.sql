-- Tabla dim_matches

CREATE TABLE
    leosmaretto_dev_coderhouse.dim_matches (
        gameId INTEGER PRIMARY KEY,
        puuid VARCHAR(80) NOT NULL,
        gameCreation TIMESTAMP NOT NULL,
        gameStartTimestamp TIMESTAMP NOT NULL,
        gameEndTimestamp TIMESTAMP NOT NULL,
        team1_win BOOLEAN NOT NULL,
        team2_win BOOLEAN NOT NULL,
        gameDurationMinutes FLOAT NOT NULL
    );

-- Tabla fact_player_stats

CREATE TABLE
    leosmaretto_dev_coderhouse.fact_player_stats (
        puuid VARCHAR(80) NOT NULL,
        summonerId VARCHAR(80) NOT NULL,
        gameId INTEGER NOT NULL,
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
        FOREIGN KEY (gameId) REFERENCES dim_matches(gameId)
    );

-- Tabla stage

CREATE TABLE
    leosmaretto_dev_coderhouse.stage (
        gameId INTEGER PRIMARY KEY,
        puuid VARCHAR(80) NOT NULL,
        gameCreation TIMESTAMP NOT NULL,
        gameStartTimestamp TIMESTAMP NOT NULL,
        gameEndTimestamp TIMESTAMP NOT NULL,
        team1_win BOOLEAN NOT NULL,
        team2_win BOOLEAN NOT NULL,
        gameDurationMinutes FLOAT NOT NULL,
        summonerId VARCHAR(80) NOT NULL,
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
    );