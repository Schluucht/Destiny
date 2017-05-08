from datetime import datetime
from random import randint

import mysql.connector
import api_call

def get_champion_list():
    champion_data = api_call.get_champion()
    champions = dict()
    for champion in champion_data['data'].values():
        champions[str(champion['id'])] = champion['name']
    return champions

def create_table(cnx):
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
        "  championId int,"
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

    for name, ddl in tables.iteritems():
        try:
            print "Creating table {}: ".format(name)
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                print "already exists."
            else:
                print err.msg
    cursor.close()
    cnx.commit()

def close_cnx(cnx):
    cnx.close()

#get all participants and tag their role
def get_participant_champ(match):
    participants = dict()
    for part in match['participants']:
        if part['timeline']['lane'] == 'JUNGLE':
            stats = part['stats']
            if stats['neutralMinionsKilled'] > 40:
                data = dict()
                data['champId'] = part['championId']
                participants[part['participantId']] = data
    return participants

#create properly a mysql connection
def get_connection_db():
    try:
        cnx = mysql.connector.connect(user='root', password='root',
                                      host='127.0.0.1', database='lol',
                                      port=3306)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print "Something is wrong with your user name or password"
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print "Database does not exist"
        else:
            print err

def extract_data(cnx):
    extract_summoners(cnx, 10)
    extract_matches(cnx, 10)
    extract_timelines(cnx)

def extract_summoners(cnx, nb_sum_needed):
    cursor = cnx.cursor()
    summoner_destack = list()
    summoners_stack = list()
    summoners_stack.append(21965576)
    while len(summoners_stack) < nb_sum_needed:
        #get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        #needed to escape potential infinite loop
        summoner_destack.append(sum_id)
        leagues = api_call.get_league_by_summoner(sum_id)

        #for each league we extract all summoner id
        for league in leagues:
            tier = league['tier']
            for entrie in league['entries']:
                if entrie['playerOrTeamId'] not in summoners_stack and len(summoners_stack) < nb_sum_needed:
                    add_player = ("INSERT IGNORE INTO players (summoner_id, account_id, tier, last_refresh) VALUES (%s, %s, %s, %s)")
                    summoners_stack.append(entrie['playerOrTeamId'])
                    player_id = int(entrie['playerOrTeamId'])
                    last_refresh = datetime.now()
                    #date format to mysql
                    last_refresh = last_refresh.strftime('%Y-%m-%d')
                    #get account id
                    account_id = api_call.get_acount_id(player_id)['accountId']
                    data_player = (player_id, account_id, tier, last_refresh)
                    #dodge duplicate primary key
                    cursor.execute(add_player, data_player)
                    cnx.commit()
    cursor.close()

def extract_matches(cnx, nb_match_needed):
    cursor = cnx.cursor()
    query = ("SELECT summoner_id from players")
    summoners_stack = list()
    cursor.execute(query)
    for account_id in cursor:
        summoners_stack.append(account_id[0])

    summoner_destack = list()
    match_stack = list()
    while len(match_stack) < nb_match_needed and len(summoners_stack) > 0:
        #get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        #needed to escape potential infinite loop
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
                if len(participants) != 2:
                    continue
                add_match = ("INSERT IGNORE INTO matches (gameId, platformId, season, timestamp) VALUES (%s, %s, %s, %s)")
                data_match = (int(matchid), match_data['platformId'], int(match_data['seasonId']), int(match_data['gameDuration']))
                cursor.execute(add_match, data_match)
    cnx.commit()
    cursor.close()

def extract_timelines(cnx):
    cursor = cnx.cursor()
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
        if len(participants) != 2:
            continue
        matchid = match_data['gameId']
        timeline = api_call.get_timeline(matchid)
        for frame in timeline['frames']:
            timestamp = frame['timestamp']
            if  timestamp > 901000:
                continue
            #stats for each minute
            for key, value in frame['participantFrames'].iteritems():
                key = int(key)
                if key in participants.keys():
                    add_stats = ("INSERT IGNORE INTO stats (gameId, timestamp, champion, level, currentGold, minionsKilled, xp, jungleMinionsKilled, x ,y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    champion = CHAMPIONS[str(participants[key]['champId'])]
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
                        add_purchase = ("INSERT IGNORE INTO itemEvent (gameId, itemId, timestamp, participant) VALUES (%s, %s, %s, %s)")
                        participant = CHAMPIONS[str(participants[events['participantId']]['champId'])]
                        data_purchase = (matchid, events['itemId'], events['timestamp'], participant)
                        cursor.execute(add_purchase, data_purchase)
                if events['type'] == 'CHAMPION_KILL':
                    if events['killerId'] in participants.keys():
                        add_kill = ("INSERT IGNORE INTO killEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                        killer = CHAMPIONS[str(participants[events['killerId']]['champId'])]
                        #to do victim as champion name, not as an id
                        data_kill = (matchid, killer, events['victimId'], events['timestamp'], events['position']['x'], events['position']['y'])
                        cursor.execute(add_kill, data_kill)
                if events['type'] == 'CHAMPION_KILL':
                    if events['victimId'] in participants.keys():
                        add_victim = ("INSERT IGNORE INTO victimEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                        victim = CHAMPIONS[str(participants[events['victimId']]['champId'])]
                        #to do victim as champion name, not as an id
                        data_victim = (matchid, events['killerId'], victim, events['timestamp'], events['position']['x'], events['position']['y'])
                        cursor.execute(add_victim, data_victim)
                if events['type'] == 'CHAMPION_KILL':
                    for participant_key in participants:
                        if participant_key in events['assistingParticipantIds']:
                            add_assist = ("INSERT IGNORE INTO assistEvent (gameId, assist, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                            assist = CHAMPIONS[str(participants[participant_key]['champId'])]
                            #to do victim as champion name, not as an id
                            data_assist = (matchid, assist, events['victimId'], events['timestamp'], events['position']['x'], events['position']['y'])
                            cursor.execute(add_assist, data_assist)
    cnx.commit()
    cursor.close()

if __name__ == '__main__':
    global CHAMPIONS
    CHAMPIONS = get_champion_list()
    CONNEXION = get_connection_db()
    create_table(CONNEXION)
    extract_data(CONNEXION)
    close_cnx(CONNEXION)
 