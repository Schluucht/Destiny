from random import randint
from datetime import datetime

import destiny.settings as settings
import destiny.main.api_call as api_call

def extract_summoners(cnx, nb_sum_needed):
    """
    Extract a list of dict where each dict represent player informations.

    :param cnx: Connexion object
    :param nb_sum_needed: int
    :return: data_summoner (list)
    """
    #initialize variable
    cursor = cnx.cursor()
    summoner_destack = list()
    summoners_stack = list()
    summoners_in_db = list()
    data_summoner = list()

    #get a random summoner
    query = ("SELECT summoner_id from players")
    cursor.execute(query)
    for sum_id in cursor:
        summoners_in_db.append(sum_id[0])
    if len(summoners_in_db) == 0:
        #initialize summoner_stack with summoner id known
        summoners_stack.append(21965576)#need to be configurable
    else:
        summoners_stack.append(summoners_in_db[randint(0, len(summoners_in_db))-1])

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
                    summoners_stack.append(entrie['playerOrTeamId'])
                    summoner_id = int(entrie['playerOrTeamId'])
                    last_refresh = datetime.now()
                    #date format to mysql
                    last_refresh = last_refresh.strftime('%Y-%m-%d')
                    #get account id
                    account_id = api_call.get_acount_id(summoner_id)['accountId']
                    data_summoner.append({"summoner_id":summoner_id, "account_id":account_id, "tier":tier, "last_refresh":last_refresh})
    
    cnx.commit()
    cursor.close()
    return data_summoner


def extract_matches(cnx, nb_match_needed):
    """
    Extract a list of dict where each dict represent match informations.

    :param cnx: Connexion object
    :param nb_match_needed: int
    :return: data_match (list)
    """
    cursor = cnx.cursor()
    summoners_stack = list()
    summoner_destack = list()
    match_stack = list()
    data_match = list()

    query = ("SELECT summoner_id from players")
    cursor.execute(query)
    for account_id in cursor:
        summoners_stack.append(account_id[0])

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
            if match_data['queueId'] == settings.TYPE_OF_GAME_NEEDED:
                matchid = int(match_data['gameId'])
                data_match.append({
                    'match_id': int(matchid), 
                    'platform_id': match_data['platformId'],
                    'season_id': int(match_data['seasonId']),
                    'game_duration': int(match_data['gameDuration'])
                    })
    cnx.commit()
    cursor.close()
    return data_match

    
def extract_timelines(cnx):
    """
    Extract a list of dict where each dict represent match timeline informations.

    :param cnx: Connexion object
    :return: matches_timeline (list)
    """
    cursor = cnx.cursor()
    query = ("SELECT game_id from matches")
    #get all match ids
    matchids = list()
    matches_timeline = list()
    cursor.execute(query)
    for game_id in cursor:
        matchids.append(game_id[0])

    # for all match ids
    for matchid in matchids:
        match_data = api_call.get_match(matchid)
        matchid = match_data['gameId']
        timeline = api_call.get_timeline(matchid)
        nb_frame_viewed = 0

        frames = list()
        for frame in timeline['frames']:
            data_frame = dict()
            stats_frame = list()
            item_event = list()
            kill_event = list()
            timestamp = frame['timestamp']
            #stats for each minute
            nb_frame_viewed = nb_frame_viewed +1
            if nb_frame_viewed < len(timeline['frames']):
                for key,value in frame['participantFrames'].items():
                    stats_frame.append({
                                  'participant_id': int(value['participantId']),
                                  'level': int(value['level']),
                                  'current_gold': int(value['currentGold']),
                                  'minions_killed': int(value['minionsKilled']),
                                  'xp': int(value['xp']),
                                  'jungle_minions_killed': int(value['jungleMinionsKilled']),
                                  'position_x': int(value['position']['x']),
                                  'position_y':int(value['position']['y'])}) 
                #event(kill,deaths,assist,ward placed) for each minute and for each jungler
                for events in frame['events']:
                    if events['type'] == 'ITEM_PURCHASED':
                        participant = events['participantId']
                        item_event.append({
                        'item_id': events['itemId'],
                        'timestamp' : events['timestamp'],
                        'participant_id': participant})

                    if events['type'] == 'CHAMPION_KILL':
                        killer = events['killerId']
                        victim = events['victimId']
                        kill_event.append({ 
                        'killer': killer, 
                        'victim': victim,
                        'assist': events['assistingParticipantIds'],
                        'timestamp' : events['timestamp'],
                        'position_x': events['position']['x'],
                        'position_y': events['position']['y']
                        })
            data_frame['timestamp'] = timestamp
            data_frame['stats'] = stats_frame
            data_frame['item_event'] = item_event
            data_frame['kill_event'] = kill_event
            frames.append(data_frame)
        matches_timeline.append({'game_id': int(matchid), 'frames': frames})

    cnx.commit()
    cursor.close()
    return matches_timeline

