import logging
import destiny.main.etl.load as load
import destiny.main.etl.extract as extract
import destiny.settings as settings
from destiny.main.bdd import clean_database, create_tables
from destiny.main.bdd.connexion import engine, Session
from destiny.utils import stream_handler


def extract_data(p_session):
    db_log.info("Extracting summoner entries from riot-games API.")
    summoners = extract.extract_summoners(p_session, settings.NB_PLAYERS_NEEDED)
    db_log.info("Loading summoners entries into the local database.")
    load.load_data(p_session, summoners)
    db_log.info("Extracting match entries from riot-games API.")
    matches = extract.extract_matches(p_session, settings.NB_MATCHES_NEEDED)
    db_log.info("Loading match entries into the local database.")
    load.load_data(p_session, matches)
    timelines = extract.extract_timelines(p_session)
    load.load_timelines(p_session, timelines)

if __name__ == '__main__':

    db_log = logging.getLogger("db_logger")
    db_log.addHandler(stream_handler)
    db_log.setLevel(logging.DEBUG)
    clean_database(engine, p_force=True)
    create_tables(engine)
    extract_data(Session)
    Session.close()
