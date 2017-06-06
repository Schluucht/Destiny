import destiny.main.etl.load as load
import destiny.main.etl.extract as extract
import destiny.settings as settings
from destiny.main.bdd import clean_database, create_tables
from destiny.main.bdd.connexion import engine, Session
from destiny.main.destinylogger import db_log
from destiny.main.bdd.models.players import Players
from destiny.main.bdd.models.participants import Participants
from destiny.main.bdd.models.assistsevents import AssistsEvents
from destiny.main.bdd.models.itemsevents import ItemsEvents
from destiny.main.bdd.models.stats import Stats
from destiny.main.bdd.models.killsevents import KillsEvents
from destiny.main.bdd.models.monstersevents import MonstersEvents
from destiny.main.bdd.models.buildingevents import BuildingEvents
from destiny.main.bdd.models.matches import Matches


def extract_data(p_session):
    """
    Extract all data entries from riot game API.

    :param p_session: Connexion object
    :return: None
    """

    db_log.info("Extracting summoner entries from riot-games API.")
    summoners = extract.extract_summoners(p_session, settings.NB_PLAYERS_NEEDED)
    db_log.info("Loading summoners entries into the local database.")
    load.load_data(p_session, summoners)

    db_log.info("Extracting matches entries from riot-games API.")
    match_id_stack = extract.extract_matches_id(p_session, settings.NB_MATCHES_NEEDED)
    matches_data = extract.extract_matches_data(match_id_stack)
    matches = extract.extract_matches(matches_data)
    load.load_data(p_session, matches)

    db_log.info("Loading matchList entries into the local database.")
    matches_by_player = extract.extract_matches_list(match_id_stack)
    load.load_data(p_session, matches_by_player)

    db_log.info("Loading participants entries into the local database.")
    participants = extract.extract_participants(matches_data)
    load.load_data(p_session, participants)

    db_log.info("Loading participants' stats entries into the local database.")
    stats_participant = extract.extract_stats_participants(matches_data)
    load.load_data(p_session, stats_participant)

    db_log.info("Loading teams' stats entries into the local database.")
    team_stats = extract.extract_team_stats(matches_data)
    load.load_data(p_session, team_stats)

    db_log.info("Loading ban' stats entries into the local database.")
    bans = extract.extract_bans(matches_data)
    load.load_data(p_session, bans)

    db_log.info("Loading timeline entries from riot-games API.")
    timelines = extract.extract_timelines(match_id_stack)
    load.load_data(p_session, timelines)

    db_log.info("Loading minute stats and events entries from riot-games API.")
    each_min_stats = extract.extract_events(p_session, match_id_stack)
    load.load_data(p_session, each_min_stats)


if __name__ == '__main__':
    clean_database(engine, p_force=True)
    create_tables(engine)
    extract_data(Session)
    Session.close()
