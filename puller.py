from datetime import datetime
from random import randint
import logging
import sys
import mysql.connector
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

import api_call
import settings
from models import Players, Matches
from models.base import Base


def get_champion_list():
    champion_data = api_call.get_champion()
    champions = dict()
    for champion in champion_data['data'].values():
        champions[str(champion['id'])] = champion['name']
    return champions


def create_tables(p_engine):
    db_log.debug("Start creating tables with engine %s." % p_engine)
    Base.metadata.create_all(p_engine)
    db_log.info("Tables created")


def close_cnx(cnx):
    cnx.close()


def role_checker(roles):
    set_supported_roles = {'TOP SOLO','MIDDLE SOLO','BOTTOM DUO_SUPPORT','BOTTOM DUO_CARRY','JUNGLE NONE'}
    if len(set(roles).difference(set_supported_roles)) != 0:
        return False
    else:
        return True


def construct_role_list(data,side):
    roles = set()
    if side == 'RED':
        for i in range (0,5):
            role = data['participants'][i]['timeline']['lane'] + ' ' + data['participants'][i]['timeline']['role']
            roles.add(role)
    elif side == 'BLUE':
        for i in range (5,10):
            role = data['participants'][i]['timeline']['lane'] + ' ' + data['participants'][i]['timeline']['role']
            roles.add(role)
    return roles


#get all participants and tag their role
def get_participant_champ(match):
    participants = {0: 'Unknown'}
    blue_side = construct_role_list(match,'BLUE')
    red_side = construct_role_list(match,'RED')
    if role_checker(blue_side) and role_checker(red_side):
        for part in match['participants']:
            participants[part['participantId']] = CHAMPIONS[str(part['championId'])]
    return participants


#create properly a mysql connection
def get_connection_db(*args, **kwargs):
    try:
        cnx = mysql.connector.connect(*args, **kwargs)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            db_log.error("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            db_log.error("Database does not exist")
        else:
            db_log.error(err)
        sys.exit(1)


def extract_data(p_session):
    extract_summoners(p_session, 5)
    extract_matches(p_session, 5)
    # orm
    # extract_timelines(cnx)


def extract_summoners(p_session, nb_sum_needed):
    summoner_destack = list()
    summoners_stack = list()
    # summoners_stack.append(85891136)
    summoners_stack.append(53668796)  # Alderiate ;)
    while len(summoners_stack) < nb_sum_needed:
        # get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        # needed to escape potential infinite loop
        summoner_destack.append(sum_id)
        leagues = api_call.get_league_by_summoner(sum_id)

        # for each league we extract all summoner id
        for league in leagues:
            tier = league['tier']
            for entrie in league['entries']:
                if entrie['playerOrTeamId'] not in summoners_stack and len(summoners_stack) < nb_sum_needed:
                    summoners_stack.append(entrie['playerOrTeamId'])
                    player_id = int(entrie['playerOrTeamId'])
                    last_refresh = datetime.now()
                    # date format to mysql
                    last_refresh = last_refresh.strftime('%Y-%m-%d')
                    # get account id
                    account_id = api_call.get_acount_id(player_id)['accountId']
                    # get the column names of the table
                    fields_player = (str(col).split(".")[-1] for col in Players.__table__.columns)
                    data_player = (player_id, account_id, tier, last_refresh)
                    # what is this comment?
                    # dodge duplicate primary key
                    # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                    new_players_entry = Players(**dict(zip(fields_player, data_player)))
                    p_session.add(new_players_entry)
        # only one commit after adding every player to the session
        p_session.commit()


def extract_matches(p_session, nb_match_needed):
    summoners_stack = list()
    for player_obj in p_session.query(Players):
        summoners_stack.append(player_obj.accountId)
    summoner_destack = list()
    match_stack = list()
    # todo use set and avoid infinite loop
    while len(match_stack) < nb_match_needed and len(summoners_stack) > 0:
        # get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        # needed to escape potential infinite loop
        summoner_destack.append(sum_id)
        account_id = api_call.get_acount_id(sum_id)
        matches_list = api_call.get_matchlist(account_id['accountId'])
        if len(matches_list) > 0:
            for match in matches_list['matches']:
                if match['gameId'] not in match_stack and len(match_stack) < nb_match_needed:
                    match_stack.append(match['gameId'])

    for match in match_stack:
        match_data = api_call.get_match(match)
        if 'queueId' in match_data:
            if match_data['queueId'] == 420:
                matchid = int(match_data['gameId'])
                participants = get_participant_champ(match_data)
                if len(participants) == 1:
                    continue
                # get the column names of the table
                fields_match = (str(col).split(".")[-1] for col in Matches.__table__.columns)
                data_match = (int(matchid), match_data['platformId'], int(match_data['seasonId']), int(match_data['gameDuration']))
                # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                new_match_entry = Matches(**dict(zip(fields_match, data_match)))
                p_session.add(new_match_entry)
    p_session.commit()


def extract_timelines(cnx):
    global CHAMPIONS

    cursor = cnx.cursor()
    # orm
    query = ("SELECT gameId from matches")
    #get all match ids
    matchids = list()
    cursor.execute(query)
    for game_id in cursor:
        matchids.append(game_id[0])

    # for all match ids
    for matchid in matchids:
        match_data = api_call.get_match(matchid)
        # extract jungler champion name
        participants = get_participant_champ(match_data)
        if len(participants) == 1:
            continue
        matchid = match_data['gameId']
        timeline = api_call.get_timeline(matchid)
        nb_frame_viewed = 0
        for frame in timeline['frames']:
            timestamp = frame['timestamp']
            #stats for each minute
            nb_frame_viewed = nb_frame_viewed +1
            if nb_frame_viewed < len(timeline['frames']):
                for key, value in frame['participantFrames'].items():
                    # orm
                    key = int(key)
                    add_stats = ("INSERT IGNORE INTO stats (gameId, timestamp, champion, level, currentGold, minionsKilled, xp, jungleMinionsKilled, x ,y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    champion = participants[key]
                    data_stats = (int(matchid),
                                  timestamp,
                                  champion,
                                  int(value['level']),
                                  int(value['currentGold']),
                                  int(value['minionsKilled']),
                                  int(value['xp']),
                                  int(value['jungleMinionsKilled']),
                                  int(value['position']['x']),
                                  int(value['position']['y']))
                    cursor.execute(add_stats, data_stats)
                #event(kill,deaths,assist,ward placed) for each minute and for each jungler
                for events in frame['events']:
                    if events['type'] == 'ITEM_PURCHASED':
                        if events['participantId'] in participants.keys():
                            # orm
                            add_purchase = ("INSERT IGNORE INTO itemEvent (gameId, itemId, timestamp, participant) VALUES (%s, %s, %s, %s)")
                            participant = participants[events['participantId']]
                            data_purchase = (matchid, events['itemId'], events['timestamp'], participant)
                            cursor.execute(add_purchase, data_purchase)

                    if events['type'] == 'CHAMPION_KILL':
                        # orm
                        if events['killerId'] in participants.keys():
                            add_kill = ("INSERT IGNORE INTO killEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                            killer = participants[events['killerId']]
                            victim = participants[events['victimId']]
                            #to do victim as champion name, not as an id
                            data_kill = (matchid, killer, victim, events['timestamp'], events['position']['x'], events['position']['y'])
                            cursor.execute(add_kill, data_kill)

                    if events['type'] == 'CHAMPION_KILL':
                        # orm
                        if events['victimId'] in participants.keys():
                            add_victim = ("INSERT IGNORE INTO victimEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                            killer = participants[events['killerId']]
                            victim = participants[events['victimId']]
                            #to do victim as champion name, not as an id
                            data_victim = (matchid, events['killerId'], victim, events['timestamp'], events['position']['x'], events['position']['y'])
                            cursor.execute(add_victim, data_victim)

                    if events['type'] == 'CHAMPION_KILL':
                        # orm
                        for participant_key in participants:
                            if participant_key in events['assistingParticipantIds']:
                                add_assist = ("INSERT IGNORE INTO assistEvent (gameId, assist, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                                assist = participants[participant_key]
                                victim = participants[events['victimId']]
                                #to do victim as champion name, not as an id
                                data_assist = (matchid, assist, victim, events['timestamp'], events['position']['x'], events['position']['y'])
                                cursor.execute(add_assist, data_assist)
    cnx.commit()
    cursor.close()


def clean_database(p_engine, p_force=False):
    """
    Drop all tables of the database.

    :param p_engine: The current used engine.
    :type p_engine: sqlalchemy.engine.Engine
    :param p_force: Don't ask for confirmation. (default: False)
    :type p_force: Boolean
    :return:
    """
    if not p_force:
        confirmation = input("Destiny is about to drop the whole database. Do you agree? y/N").strip()
        if confirmation != 'y':
            db_log.info("DB won't be empty.")
            return
    db_log.debug("Start droping tables with engine %s." % p_engine)
    Base.metadata.drop_all(p_engine)
    db_log.info("Tables droped")


if __name__ == '__main__':
    global CHAMPIONS
    CHAMPIONS = get_champion_list()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    db_log = logging.getLogger("db_logger")
    db_log.addHandler(stream_handler)
    db_log.setLevel(logging.DEBUG)

    connection_string = ('%s%s://%s:%s@%s:%s/%s' %
                           (settings.DB_DIALECT,
                            "+" + settings.DB_DRIVER if settings.DB_DRIVER is not "" else settings.DB_DRIVER,
                            settings.DB_USER,
                            settings.DB_PASSWORD,
                            settings.DB_HOST,
                            settings.DB_PORT,
                            settings.DB_NAME))

    db_log.debug("Connection string: %s" % connection_string)
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)()

    CONNEXION = get_connection_db(user=settings.DB_USER, password=settings.DB_PASSWORD,
                            host=settings.DB_HOST, database=settings.DB_NAME,
                            port=settings.DB_PORT)

    clean_database(engine, p_force=True)
    create_tables(engine)

    extract_data(Session)

    close_cnx(CONNEXION)
