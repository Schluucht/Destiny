from datetime import datetime
from random import randint
import destiny.main.api_call as api_call
import logging
import sys
import mysql.connector
import destiny.main.bdd.models.model as model
import destiny.main.etl.load as load
import destiny.main.etl.extract as extract
import destiny.settings as settings
import destiny.main.bdd.connexion as connexion

def extract_data(cnx):
    summoners = extract.extract_summoners(cnx, settings.NB_PLAYERS_NEEDED)
    load.load_summoners(cnx, summoners)
    matches = extract.extract_matches(cnx, settings.NB_MATCHES_NEEDED)
    load.load_matches(cnx, matches)
    timelines = extract.extract_timelines(cnx)
    load.load_timelines(cnx, timelines)

if __name__ == '__main__':
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    db_log = logging.getLogger("db_logger")
    db_log.addHandler(stream_handler)
    db_log.setLevel(logging.DEBUG)

    CONNEXION = connexion.get_connection_db(user=settings.DB_USER, password=settings.DB_PASSWORD,
                            host=settings.DB_HOST, database=settings.DB_NAME,
                            port=settings.DB_PORT)

    model.create_table(CONNEXION)
    extract_data(CONNEXION)

    connexion.clean_database(CONNEXION)
    connexion.close_cnx(CONNEXION)
