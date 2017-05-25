from datetime import datetime

import pytest

from destiny.main.bdd.models.assistevent import AssistEvent
from destiny.main.bdd.models.itemevent import ItemEvent
from destiny.main.bdd.models.killevent import KillEvent
from destiny.main.bdd.models.matches import Matches
from destiny.main.bdd.models.participant import Participant
from destiny.main.bdd.models.players import Players
from destiny.main.bdd import clean_database, create_tables
from destiny.main.bdd.connexion import engine, Session
from destiny.main.bdd.models.stats import Stats
from destiny.main.etl.load import load_data


@pytest.fixture(scope="module")
def database(p_session):
    create_tables(engine)
    yield None
    p_session.close()
    clean_database(engine, p_force=True)


@pytest.fixture(scope="module")
def p_session():
    return Session


# testing check it was added to the database be carefull with the fields
def test_load_data(database, p_session):
    """
    For each model try an insertion in the database

    :param p_session: Session object.
    :param database: None. This call the fixture in order to setup and teardown test.
    :return: None
    """
    data_players = [Players(summonerId=1, accountId=1, tier="Tier", lastRefresh=datetime.now())]
    data_stats = [Stats(idStats=1, gameId=1, timestamp=1, participantId="participant", level=1, currentGold=1,
                        minionsKilled=1, jungleMinionsKilled=1, xp=1, x=1, y=1)]
    data_assistevent = [AssistEvent(gameId=1, assist="assist", victim="victim", timestamp=1, x=1, y=1)]
    data_itemevent = [ItemEvent(gameId=1, itemId=1, timestamp=1, participantId=1)]
    data_killevent = [KillEvent(gameId=1, killerId=1, victimId=1, timestamp=1, x=1, y=1)]
    data_matches = [Matches(gameId=1, platformId="platform", season=1, timestamp=1)]
    data_participants = [Participant(gameId=1, participantId=1, role="role", championId=1)]

    load_data(p_session, data_players)
    load_data(p_session, data_stats)
    load_data(p_session, data_assistevent)
    load_data(p_session, data_itemevent)
    load_data(p_session, data_killevent)
    load_data(p_session, data_matches)
    load_data(p_session, data_participants)

    db_players = p_session.query(Players).one()
    db_stats = p_session.query(Stats).one()
    db_assistevent = p_session.query(AssistEvent).one()
    db_itemevent = p_session.query(ItemEvent).one()
    db_killevent = p_session.query(KillEvent).one()
    db_matches = p_session.query(Matches).one()
    db_participants = p_session.query(Participant).one()
    assert db_players == data_players[-1]
    assert db_stats == data_stats[-1]
    assert db_assistevent == data_assistevent[-1]
    assert db_itemevent == data_itemevent[-1]
    assert db_killevent == data_killevent[-1]
    assert db_matches == data_matches[-1]
    assert db_participants == data_participants[-1]