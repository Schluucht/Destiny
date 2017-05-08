import os
import sys
import mysql.connector

from datetime import datetime, date
from mysql.connector import errorcode
from random import randint
from api_call import get_league_by_summoner, get_acount_id, get_matchlist, get_match, get_timeline

CHAMPIONS = {"62":"Wukong","24":"Jax","35":"Shaco","19":"Warwick","76":"Nidalee","143":"Zyra","240":"Kled","63":"Brand","33":"Rammus","420":"Illaoi","42":"Corki","201":"Braum","34":"Anivia","23":"Tryndamere","21":"Miss Fortune","83":"Yorick","101":"Xerath","15":"Sivir","92":"Riven","61":"Orianna","41":"Gangplank","54":"Malphite","78":"Poppy","30":"Karthus","126":"Jayce","53":"Blitzcrank","48":"Trundle","113":"Sejuani","104":"Graves","236":"Lucian","150":"Gnar","99":"Lux","102":"Shyvana","58":"Renekton","114":"Fiora","222":"Jinx","429":"Kalista","105":"Fizz","38":"Kassadin","37":"Sona","8":"Vladimir","112":"Viktor","203":"Kindred","69":"Cassiopeia","57":"Maokai","412":"Thresh","10":"Kayle","120":"Hecarim","121":"Kha'Zix","2":"Olaf","115":"Ziggs","134":"Syndra","36":"Dr. Mundo","43":"Karma","1":"Annie","84":"Akali","89":"Leona","157":"Yasuo","85":"Kennen","107":"Rengar","13":"Ryze","98":"Shen","154":"Zac","80":"Pantheon","50":"Swain","432":"Bard","14":"Sion","67":"Vayne","75":"Nasus","4":"Twisted Fate","31":"Cho'Gath","77":"Udyr","25":"Morgana","427":"Ivern","106":"Volibear","51":"Caitlyn","122":"Darius","56":"Nocturne","68":"Rumble","26":"Zilean","268":"Azir","131":"Diana","72":"Skarner","17":"Teemo","6":"Urgot","32":"Amumu","3":"Galio","74":"Heimerdinger","22":"Ashe","161":"Vel'Koz","27":"Singed","163":"Taliyah","110":"Varus","29":"Twitch","86":"Garen","20":"Nunu","11":"Master Yi","60":"Elise","12":"Alistar","55":"Katarina","245":"Ekko","82":"Mordekaiser","117":"Lulu","164":"Camille","266":"Aatrox","119":"Draven","223":"Tahm Kench","9":"Fiddlesticks","91":"Talon","5":"Xin Zhao","136":"Aurelion Sol","64":"Lee Sin","44":"Taric","90":"Malzahar","127":"Lissandra","18":"Tristana","421":"Rek'Sai","39":"Irelia","59":"Jarvan IV","267":"Nami","202":"Jhin","16":"Soraka","45":"Veigar","40":"Janna","111":"Nautilus","28":"Evelynn","79":"Gragas","238":"Zed","254":"Vi","96":"Kog'Maw","103":"Ahri","133":"Quinn","7":"LeBlanc","81":"Ezreal"}

# Todo faire des objets qui encapsulent les requetes
# Faire un check des headers pour les calls a l'API


def create_table(cnx):
    cursor = cnx.cursor()
    TABLES = {}
    TABLES['players'] = (
        "CREATE TABLE IF NOT EXISTS players("
        "  summoner_id bigint NOT NULL,"
        "  account_id bigint NOT NULL,"
        "  tier char(12),"
        "  last_refresh date NOT NULL,"
        "  PRIMARY KEY (summoner_id)"
        ") ENGINE=InnoDB")

    TABLES['match'] = (
        "CREATE TABLE IF NOT EXISTS matches("
        "  gameId bigint NOT NULL,"
        "  platformId char(9),"
        "  season int,"
        "  timestamp bigint,"
        "  PRIMARY KEY (gameId)"
        ") ENGINE=InnoDB")

    TABLES['participant'] = (
        "CREATE TABLE IF NOT EXISTS participant("
        "  gameId bigint NOT NULL,"
        "  participantId int,"
        "  championId int,"
        "  PRIMARY KEY (gameId, participantId)"
        ") ENGINE=InnoDB")

    TABLES['stats'] = (
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

    TABLES['itemEvent'] = (
        "CREATE TABLE IF NOT EXISTS itemEvent("
        "  gameId bigint NOT NULL,"
        "  itemId int,"
        "  timestamp int,"
        "  participant char(50),"
        "  PRIMARY KEY (gameId,participant,timestamp)"
        ") ENGINE=InnoDB")

    TABLES['killEvent'] = (
        "CREATE TABLE IF NOT EXISTS killEvent("
        "  gameId bigint NOT NULL,"
        "  killer char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,killer,victim)"
        ") ENGINE=InnoDB")

    TABLES['assistEvent'] = (
        "CREATE TABLE IF NOT EXISTS assistEvent("
        "  gameId bigint NOT NULL,"
        "  assist char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,assist,victim)"
        ") ENGINE=InnoDB")

    TABLES['victimEvent'] = (
        "CREATE TABLE IF NOT EXISTS victimEvent("
        "  gameId bigint NOT NULL,"
        "  killer char(50),"
        "  victim char(50),"
        "  timestamp int,"
        "  x int,"
        "  y int,"
        "  PRIMARY KEY (gameId,timestamp,killer,victim)"
        ") ENGINE=InnoDB")

    for name, ddl in TABLES.iteritems():
        try:
            print("Creating table {}: ".format(name))
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
    cursor.close()
    cnx.commit()


def close_cnx(cnx):
    cnx.close()


#get all participants and tag their role
def getParticipantChamp(match):
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
        cnx = mysql.connector.connect(user='', password='',
                              host='127.0.0.1', database='lol',
                              port=3306)
        return cnx
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)


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
        sum_id = summoners_stack[randint(0,len(summoners_stack))-1]
        #needed to escape potential infinite loop
        summoner_destack.append(sum_id)
        leagues = get_league_by_summoner(sum_id)

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
                    account_id = get_acount_id(player_id)['accountId']
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
    for (account_id) in cursor:
        summoners_stack.append(account_id[0])

    summoner_destack = list()
    match_destack = list()
    match_stack = list()
    while len(match_stack) < nb_match_needed and len(summoners_stack) > 0 :
        #get random summoner id in stack
        sum_id = summoners_stack[randint(0,len(summoners_stack))-1]
        #needed to escape potential infinite loop
        summoner_destack.append(sum_id)
        account_id = get_acount_id(sum_id)
        matchesList = get_matchlist(account_id['accountId'])
        if len(matchesList) > 0:
            for match in matchesList['matches']:
                if match['gameId'] not in match_stack and len(match_stack) < nb_match_needed:
                    match_stack.append(match['gameId'])

    for match in match_stack:
        m = get_match(match)
        if 'queueId' in m:
            if m['queueId'] == 420:
                matchid = int(m['gameId'])
                participants = getParticipantChamp(m)
                if len(participants) != 2:
                    continue
                add_match = ("INSERT IGNORE INTO matches (gameId, platformId, season, timestamp) VALUES (%s, %s, %s, %s)")
                data_match = (int(matchid), m['platformId'], int(m['seasonId']), int(m['gameDuration']))
                cursor.execute(add_match, data_match)     
    cnx.commit()
    cursor.close()


def extract_timelines(cnx):
    global CHAMPIONS

    cursor = cnx.cursor()
    query = ("SELECT gameId from matches")
    #get all match ids
    matchids = list()
    cursor.execute(query)
    for (gameId) in cursor:
        matchids.append(gameId[0])

    # for all match ids
    for matchid in matchids:
        m = get_match(matchid)
        # extract jungler champion name
        participants = getParticipantChamp(m)
        if len(participants) != 2:
            continue
        matchid = m['gameId']
        timeline = get_timeline(matchid)
        for frame in timeline['frames']:
            timestamp = frame['timestamp']
            #limit to first 15min
            if  timestamp > 901000:
                continue
            #stats for each minute
            for k,v in frame['participantFrames'].iteritems():
                k = int(k)
                if k in participants.keys():
                    add_stats = ("INSERT IGNORE INTO stats (gameId, timestamp, champion, level, currentGold, minionsKilled, xp, jungleMinionsKilled, x ,y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    champion = CHAMPIONS[str(participants[k]['champId'])]
                    data_stats = (int(matchid), 
                        timestamp, 
                        champion, 
                        int(v['level']), 
                        int(v['currentGold']), 
                        int(v['minionsKilled']), 
                        int(v['xp']), 
                        int(v['jungleMinionsKilled']), 
                        int(v['position']['x']), 
                        int(v['position']['y']))
                    cursor.execute(add_stats, data_stats)
            #event(kill,deaths,assist,ward placed) for each minute and for each jungler
            for events in frame['events']:
                if events['type'] == 'ITEM_PURCHASED':
                    if events['participantId'] in participants.keys():
                        add_purchase = ("INSERT IGNORE INTO itemEvent (gameId, itemId, timestamp, participant) VALUES (%s, %s, %s, %s)")
                        participant = CHAMPIONS[str(participants[events['participantId']]['champId'])]
                        data_purchase = (matchid, events['itemId'] ,events['timestamp'],participant )
                        cursor.execute(add_purchase, data_purchase)
                if events['type'] == 'CHAMPION_KILL':
                    if events['killerId'] in participants.keys():
                        add_kill = ("INSERT IGNORE INTO killEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                        killer = CHAMPIONS[str(participants[events['killerId']]['champId'])]
                        #to do victim as champion name, not as an id
                        data_kill = (matchid, killer, events['victimId'], events['timestamp'], events['position']['x'], events['position']['y'] )
                        cursor.execute(add_kill, data_kill)
                if events['type'] == 'CHAMPION_KILL':
                    if events['victimId'] in participants.keys():
                        add_victim = ("INSERT IGNORE INTO victimEvent (gameId, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                        victim = CHAMPIONS[str(participants[events['victimId']])]
                        #to do victim as champion name, not as an id
                        data_victim = (matchid, assist, events['killerId'], events['timestamp'], events['position']['x'], events['position']['y'] )
                        cursor.execute(add_victim, data_victim)
                if events['type'] == 'CHAMPION_KILL':
                    for p in participants.keys():
                        if p in events['assistingParticipantIds']:
                            add_assist = ("INSERT IGNORE INTO assistEvent (gameId, assist, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                            assist = CHAMPIONS[str(participants[p]['champId'])]
                            #to do victim as champion name, not as an id
                            data_assist = (matchid, assist, events['victimId'], events['timestamp'], events['position']['x'], events['position']['y'] )
                            cursor.execute(add_assist, data_assist)
    cnx.commit()
    cursor.close()

if __name__ == '__main__':
    cnx = get_connection_db()
    create_table(cnx)
    extract_data(cnx)
    close_cnx(cnx)
 