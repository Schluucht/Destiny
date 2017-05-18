from datetime import datetime
from random import randint
import api_call
import logging
import sys
import mysql.connector
import model
import load
import extract
import settings
import connexion

def extract_data(cnx):
    summoners = extract.extract_summoners(cnx, 10)
    load.load_summoners(cnx, summoners)
    matches = extract.extract_matches(cnx, 10)
    load.load_matches(cnx, matches)
    # extract_timelines(cnx)

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
