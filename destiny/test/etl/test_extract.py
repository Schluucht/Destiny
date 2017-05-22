from random import randint
from datetime import datetime

import destiny.settings as settings
import destiny.main.api_call as api_call
from destiny.main.bdd.models import Players
from destiny.main.bdd.models.itemevent import ItemEvent
from destiny.main.bdd.models.killevent import KillEvent
from destiny.main.bdd.models.matches import Matches
from destiny.main.bdd.models.stats import Stats
from destiny.main.destinyexception import DestinyException
from destiny.main.destinylogger import ext_log


def extract_summoners(p_session, nb_sum_needed):
    """
    Extract a list of `Players` objects from riot games API.

    :param p_session: Connexion object
    :param nb_sum_needed: int
    :return: data_summoner (list)
    """
    # initialize variable
    summoners_stack = set()
    data_summoner = list()
    # initialize summoner_stack with summoner id known
    summoners_stack.add(21965576)  # need to be configurable
    # summoners_stack.add(1)  # need to be configurable

    if len(summoners_stack) == 0:
        one_summoner = p_session.query(Players.summonerId).one()
        summoners_stack.add(one_summoner)

    while len(summoners_stack) < nb_sum_needed:
        try:
            # get random summoner id in stack
            sum_id = summoners_stack.pop()
        except KeyError:
            s_exce = "No summoner retrieved"
            ext_log.error(s_exce)
            raise DestinyException(s_exce)
        # needed to escape potential infinite loop
        leagues = api_call.get_league_by_summoner(sum_id)

        # for each league we extract all summoner id
        for league in leagues:
            tier = league['tier']
            for entrie in league['entries']:
                if entrie['playerOrTeamId'] not in summoners_stack and len(summoners_stack) < nb_sum_needed:
                    summoners_stack.add(entrie['playerOrTeamId'])
                    summoner_id = int(entrie['playerOrTeamId'])
                    last_refresh = datetime.now()
                    # date format to mysql
                    last_refresh = last_refresh.strftime('%Y-%m-%d')
                    # get account id
                    account_id = api_call.get_acount_id(summoner_id)['accountId']
                    fields_player = (str(col).split(".")[-1] for col in Players.__table__.columns)
                    tpl_data_player = (summoner_id, account_id, tier, last_refresh)
                    # todo make it dynamic with the dictzip thing
                    data_summoner.append(Players(**dict(zip(fields_player, tpl_data_player))))
    return data_summoner


def extract_matches(p_session, nb_match_needed):
    """
    Extract a list of `Matches` objects from riot game API.

    :param p_session: Connexion object
    :param nb_match_needed: int
    :return: data_match (list)
    """
    match_stack = list()
    data_match = list()

    # get the summoner Id and flatten the resulting list into a tuple of size `number of summoner ids`
    summoners_stack = sum(p_session.query(Players.summonerId), ())

    while len(match_stack) < nb_match_needed and len(summoners_stack) > 0:
        # get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        # needed to escape potential infinite loop
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
                tpl_data_match = (
                    int(matchid),
                    match_data['platformId'],
                    int(match_data['seasonId']),
                    int(match_data['gameDuration'])
                )
                # get the column names of the table
                fields_match = (str(col).split(".")[-1] for col in Matches.__table__.columns)
                # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                new_match_entry = Matches(**dict(zip(fields_match, tpl_data_match)))
                data_match.append(new_match_entry)

    return data_match

    
def extract_timelines(p_session):
    """
    Extract a list of matches timelines which contain:
        - A list of frames where each frame is:
            - A dict where the entries are:
                - stats: the list of Stats objects for the

    :param p_session: Connexion object
    :return: matches_timeline (list)
    """
    # get all match ids
    matchids = sum(p_session.query(Matches.gameId), ())
    matches_timeline = list()

    # for all match ids
    for matchid in matchids:
        match_data = api_call.get_match(matchid)
        matchid = match_data['gameId']
        timeline = api_call.get_timeline(matchid)
        nb_frame_viewed = 0

        frames = list()
        # for each frame of the timeline of the match
        for frame in timeline['frames']:
            dict_data_frame = dict()
            l_stats_frame = list()
            l_item_event = list()
            l_kill_event = list()
            timestamp = frame['timestamp']
            # stats for each minute
            nb_frame_viewed += 1
            if nb_frame_viewed < len(timeline['frames']):
                for _, value in frame['participantFrames'].items():
                    # get the column names of the table
                    fields_stats = (str(col).split(".")[-1] for col in Stats.__table__.columns)
                    # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                    data_stats = (
                        None,  # autoincrement idStats
                        matchid,
                        timestamp,
                        int(value['participantId']),
                        int(value['level']),
                        int(value['currentGold']),
                        int(value['minionsKilled']),
                        int(value['jungleMinionsKilled']),
                        int(value['xp']),
                        int(value['position']['x']),
                        int(value['position']['y'])
                    )
                    new_stats_entry = Stats(**dict(zip(fields_stats, data_stats)))
                    l_stats_frame.append(new_stats_entry)
                # event(kill,deaths,assist,ward placed) for each minute and for each jungler
                for events in frame['events']:
                    if events['type'] == 'ITEM_PURCHASED':
                        participant = events['participantId']
                        fields_purchase = (str(col).split(".")[-1] for col in ItemEvent.__table__.columns)
                        data_purchase = (
                            matchid,
                            events['itemId'],
                            events['timestamp'],
                            participant
                        )
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_purchase_entry = ItemEvent(**dict(zip(fields_purchase, data_purchase)))
                        l_item_event.append(new_purchase_entry)
                    elif events['type'] == 'CHAMPION_KILL':
                        killer_id = events['killerId']
                        victim_id = events['victimId']
                        # todo something with this list of assists
                        # we can concatenate the IDs in order to create an ID for the table assist
                        l_assist_ids = events['assistingParticipantIds']
                        kill_data = (
                            matchid,
                            killer_id,
                            victim_id,
                            events['timestamp'],
                            events['position']['x'],
                            events['position']['y']
                        )
                        # get the column names of the table
                        fields_kill = (str(col).split(".")[-1] for col in KillEvent.__table__.columns)
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_kill_entry = KillEvent(**dict(zip(fields_kill, kill_data)))
                        l_kill_event.append(new_kill_entry)
            dict_data_frame['stats'] = l_stats_frame
            dict_data_frame['item_event'] = l_item_event
            dict_data_frame['kill_event'] = l_kill_event
            frames.append(dict_data_frame)
        matches_timeline.append(frames)

    return matches_timeline

