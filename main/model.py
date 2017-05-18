import mysql.connector
import logging
import settings

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

db_log = logging.getLogger("db_logger")
db_log.addHandler(stream_handler)
db_log.setLevel(logging.DEBUG)

def create_table(cnx):
    """
    Create all necessary tables of database.

    :param cnx: Connexion object
    :return: None
    """
    cursor = cnx.cursor()
    tables = {}
    tables['players'] = (
        "CREATE TABLE IF NOT EXISTS players("
        "  summoner_id bigint NOT NULL,"
        "  account_id bigint NOT NULL,"
        "  tier char(12),"
        "  last_refresh date NOT NULL,"
        "  PRIMARY KEY (summoner_id)"
        ") ENGINE=InnoDB")

    tables['match'] = (
        "CREATE TABLE IF NOT EXISTS matches("
        "  gameId bigint NOT NULL,"
        "  platformId char(9),"
        "  season int,"
        "  timestamp bigint,"
        "  PRIMARY KEY (gameId)"
        ") ENGINE=InnoDB")

    tables['participant'] = (
        "CREATE TABLE IF NOT EXISTS participant("
        "  gameId bigint NOT NULL,"
        "  participantId int,"
        "  role char(20),"
        "  championId char(50),"
        "  PRIMARY KEY (gameId, participantId)"
        ") ENGINE=InnoDB")

    tables['stats'] = (
        "CREATE TABLE IF NOT EXISTS stats("
        "  idstats bigint NOT NULL AUTO_INCREMENT,"
        "  gameId bigint NOT NULL,"
        "  timestamp bigint NOT NULL,"
        "  champion char(50),"
        "  level int,"
        "  currentGold int,"
        "  minionsKilled int,"
        "  xp int,"
        "  jungleMinionsKilled int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (idstats)"
        ") ENGINE=InnoDB")

    tables['itemEvent'] = (
        "CREATE TABLE IF NOT EXISTS itemEvent("
        "  gameId bigint NOT NULL,"
        "  itemId int,"
        "  timestamp int,"
        "  participant char(50),"
        "  PRIMARY KEY (gameId,participant,timestamp)"
        ") ENGINE=InnoDB")

    tables['killEvent'] = (
        "CREATE TABLE IF NOT EXISTS killEvent("
        "  gameId bigint NOT NULL,"
        "  killer char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,killer,victim)"
        ") ENGINE=InnoDB")

    tables['assistEvent'] = (
        "CREATE TABLE IF NOT EXISTS assistEvent("
        "  gameId bigint NOT NULL,"
        "  assist char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,assist,victim)"
        ") ENGINE=InnoDB")

    tables['victimEvent'] = (
        "CREATE TABLE IF NOT EXISTS victimEvent("
        "  gameId bigint NOT NULL,"
        "  killer char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,killer,victim)"
        ") ENGINE=InnoDB")

    for name, ddl in tables.items():
        try:
            db_log.info("Creating table {}: ".format(name))
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                db_log.error("already exists.")
            else:
                db_log.error(err.msg)
            sys.exit(1)
    cursor.close()
    cnx.commit()

