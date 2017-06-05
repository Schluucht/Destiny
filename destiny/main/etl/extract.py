from random import randint
from datetime import datetime

from sqlalchemy import func

import destiny.utils as utils
import destiny.main.api_call as api_call
from destiny.main.bdd.models import Players
from destiny.main.bdd.models.participants import Participants
from destiny.main.bdd.models.participantstats import ParticipantStats
from destiny.main.bdd.models.timelines import Timelines
from destiny.main.bdd.models.events import Events
from destiny.main.bdd.models.wardsevents import WardsEvents
from destiny.main.bdd.models.itemsevents import ItemsEvents
from destiny.main.bdd.models.killsevents import KillsEvents
from destiny.main.bdd.models.buildingevents import BuildingEvents
from destiny.main.bdd.models.monstersevents import MonstersEvents
from destiny.main.bdd.models.assistsevents import AssistsEvents
from destiny.main.bdd.models.matches import Matches 
from destiny.main.bdd.models.bans import Bans
from destiny.main.bdd.models.listmatches import ListMatches
from destiny.main.bdd.models.teamstats import TeamStats
from destiny.main.bdd.models.stats import Stats
from destiny.main.destinyexception import DestinyException
from destiny.main.destinylogger import ext_log

def extract_master_sum_id():
    """
    Extract random player from master queue.

    :return: master_summoner_id (int)
    """
    # think about season reseting and master league being empty
    res_request = api_call.get_master()
    master_summoner_id = res_request['entries'][randint(0, len(res_request['entries']))-1]
    return master_summoner_id['playerOrTeamId']


def extract_summoners(p_session, nb_sum_needed):
    """
    Extract a list of `Players` objects from riot games API.

    :param p_session: Connexion object
    :param nb_sum_needed: int
    :return: data_summoner (list)
    """
    # initialize variable
    summoners_stack = set()
    data_summoner = set()
    # initialize summoner_stack with summoner id known
    random_summoner = extract_master_sum_id()
    summoners_stack.add(random_summoner)  # need to be configurable

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
            for entry in league['entries']:
                if entry['playerOrTeamId'] not in summoners_stack and len(summoners_stack) < nb_sum_needed:
                    try:
                        summoner_id = entry['playerOrTeamId']
                        summoners_stack.add(summoner_id)
                    except KeyError:
                        s_exce = "No playerOrTeamId key found in this entry"
                        ext_log.error(s_exce)
                        raise DestinyException(s_exce)
                    last_refresh = datetime.now()
                    # date format to mysql
                    last_refresh = last_refresh.strftime('%Y-%m-%d')
                    # get account id
                    account_id = api_call.get_acount_id(summoner_id).get('accountId')
                    fields_player = (str(col).split(".")[-1] for col in Players.__table__.columns)
                    tpl_data_player = (summoner_id, account_id, tier, last_refresh)
                    # todo make it dynamic with the dictzip thing
                    data_summoner.add(Players(**dict(zip(fields_player, tpl_data_player))))
    return data_summoner


def extract_matches_data(match_id_stack):
    """
    Extract a list of `Matches` objects from riot game API.

    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_match = list()
    for match in match_id_stack:
        matchid = match[1]
        match_data = api_call.get_match(matchid)
        # get the column names of the table
        data_match.append(match_data)
    return data_match


def extract_matches(matches):
    """
    Extract a list of `Matches` objects from riot game API.

    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_match = set()
    for match in matches:
        tpl_data_match = (
            match.get('gameId'),
            match.get('platformId'),
            match.get('seasonId'),
            match.get('gameVersion'),
            match.get('gameDuration')
        )
        # get the column names of the table
        fields_match = (str(col).split(".")[-1] for col in Matches.__table__.columns)
        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
        new_match_entry = Matches(**dict(zip(fields_match, tpl_data_match)))
        data_match.add(new_match_entry)
    return data_match


def extract_team_stats(matches):
    """
    Extract a list of `Matches` objects from riot game API.

    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_team_stats = set()
    for match in matches:
        gameId = match['gameId']
        for team in match['teams']:
            tpl_team_stats = (
                gameId,
                team.get('teamId'),
                team.get('firstDragon'),
                team.get('firstInhibitor'),
                team.get('baronKills'),
                team.get('firstRiftHerald'),
                team.get('firstBaron'),
                team.get('riftHeraldKills'),
                team.get('firstBlood'),
                team.get('firstTower'),
                team.get('inhibitorKills'),
                team.get('towerKills'),
                team.get('win'),
                team.get('dragonKills')
            )
            # get the column names of the table
            fields_team_stats = (str(col).split(".")[-1] for col in TeamStats.__table__.columns)
            # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
            new_team_stats_entry = TeamStats(**dict(zip(fields_team_stats, tpl_team_stats)))
            data_team_stats.add(new_team_stats_entry)
    return data_team_stats


def extract_bans(matches):
    """
    Extract a list of `Matches` objects from riot game API.

    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_bans = set()
    for match in matches:
        gameId = match['gameId']
        for team in match['teams']:
            for ban in team['bans']:
                tpl_ban = (
                    gameId,
                    team.get('teamId'),
                    ban.get('pickTurn'),
                    ban.get('championId'),
                )
                # get the column names of the table
                fields_bans = (str(col).split(".")[-1] for col in Bans.__table__.columns)
                # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                new_bans_entry = Bans(**dict(zip(fields_bans, tpl_ban)))
                data_bans.add(new_bans_entry)

    return data_bans


def extract_participants(matches):
    """
    Extract a list of `Matches` objects from riot game API.
    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_match = set()
    for match in matches:
        gameId = match['gameId']
        for participant in match['participants']:
            tpl_data_participant = (
                gameId,
                participant.get('participantId'),
                participant.get('teamId'),
                participant.get('highestAchievedSeasonTier'),
                participant.get('championId'),
                participant.get('spell1Id'),
                participant.get('spell2Id')
            )
            # get the column names of the table
            fields_participant = (str(col).split(".")[-1] for col in Participants.__table__.columns)
            # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
            new_part_entry = Participants(**dict(zip(fields_participant, tpl_data_participant)))
            data_match.add(new_part_entry)
    return data_match


def extract_stats_participants(matches):
    """
    Extract a list of `Matches` objects from riot game API.
    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_participant = set()
    for match in matches:
        gameId = match['gameId']
        for participant in match['participants']:
            tpl_data_participant = (
                gameId,
                participant.get('stats').get('participantId'),
                participant.get('stats').get('physicalDamageDealt'),
                participant.get('stats').get('neutralMinionsKilledTeamJungle'),
                participant.get('stats').get('magicDamageDealt'),
                participant.get('stats').get('totalPlayerScore'),
                participant.get('stats').get('deaths'),
                participant.get('stats').get('win'),
                participant.get('stats').get('neutralMinionsKilledEnemyJungle'),
                participant.get('stats').get('largestCriticalStrike'),
                participant.get('stats').get('totalDamageDealt'),
                participant.get('stats').get('magicDamageDealtToChampions'),
                participant.get('stats').get('visionWardsBoughtInGame'),
                participant.get('stats').get('damageDealtToObjectives'),
                participant.get('stats').get('largestKillingSpree'),
                participant.get('stats').get('item1'),
                participant.get('stats').get('quadraKills'),
                participant.get('stats').get('totalTimeCrowdControlDealt'),
                participant.get('stats').get('longestTimeSpentLiving'),
                participant.get('stats').get('wardsKilled'),
                participant.get('stats').get('firstTowerAssist'),
                participant.get('stats').get('firstTowerKill'),
                participant.get('stats').get('item2'),
                participant.get('stats').get('item3'),
                participant.get('stats').get('item0'),
                participant.get('stats').get('firstBloodAssist'),
                participant.get('stats').get('visionScore'),
                participant.get('stats').get('wardsPlaced'),
                participant.get('stats').get('item4'),
                participant.get('stats').get('item5'),
                participant.get('stats').get('item6'),
                participant.get('stats').get('turretKills'),
                participant.get('stats').get('tripleKills'),
                participant.get('stats').get('damageSelfMitigated'),
                participant.get('stats').get('champLevel'),
                participant.get('stats').get('firstInhibitorKill'),
                participant.get('stats').get('goldEarned'),
                participant.get('stats').get('magicalDamageTaken'),
                participant.get('stats').get('kills'),
                participant.get('stats').get('doubleKills'),
                participant.get('stats').get('trueDamageTaken'),
                participant.get('stats').get('firstInhibitorAssist'),
                participant.get('stats').get('assists'),
                participant.get('stats').get('unrealKills'),
                participant.get('stats').get('neutralMinionsKilled'),
                participant.get('stats').get('objectivePlayerScore'),
                participant.get('stats').get('combatPlayerScore'),
                participant.get('stats').get('damageDealtToTurrets'),
                participant.get('stats').get('physicalDamageDealtToChampions'),
                participant.get('stats').get('goldSpent'),
                participant.get('stats').get('trueDamageDealt'),
                participant.get('stats').get('trueDamageDealtToChampions'),
                participant.get('stats').get('pentaKills'),
                participant.get('stats').get('totalHeal'),
                participant.get('stats').get('totalMinionsKilled'),
                participant.get('stats').get('firstBloodKill'),
                participant.get('stats').get('largestMultiKill'),
                participant.get('stats').get('sightWardsBoughtInGame'),
                participant.get('stats').get('totalDamageDealtToChampions'),
                participant.get('stats').get('totalUnitsHealed'),
                participant.get('stats').get('inhibitorKills'),
                participant.get('stats').get('totalScoreRank'),
                participant.get('stats').get('totalDamageTaken'),
                participant.get('stats').get('killingSprees'),
                participant.get('stats').get('timeCCingOthers'),
                participant.get('stats').get('physicalDamageTaken')
            )
            # get the column names of the table
            fields_participant = (str(col).split(".")[-1] for col in ParticipantStats.__table__.columns)
            # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
            new_part_entry = ParticipantStats(**dict(zip(fields_participant, tpl_data_participant)))
            data_participant.add(new_part_entry)
    return data_participant

def extract_matches_list(match_id_stack):
    """
    Extract a list of `Matches` objects from riot game API.

    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_match = set()

    for match in match_id_stack:
        matchid = int(match[1])
        tpl_data_list_matches = (
            match[0],
            matchid
            )
        # get the column names of the table
        fields_list_match = (str(col).split(".")[-1] for col in ListMatches.__table__.columns)
        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
        new_list_match_entry = ListMatches(**dict(zip(fields_list_match, tpl_data_list_matches)))
        data_match.add(new_list_match_entry)
    return data_match


def extract_matches_id(p_session, nb_match_needed):
    match_stack = set()
    summoners_stack = [sum_id[0] for sum_id in p_session.query(Players.summonerId).all()]
    while len(match_stack) < nb_match_needed and len(summoners_stack) > 0:
        # get random summoner id in stack
        sum_id = summoners_stack[randint(0, len(summoners_stack))-1]
        summoners_stack.remove(sum_id)
        account_id = api_call.get_acount_id(sum_id)
        matches_list = api_call.get_matchlist(account_id.get('accountId'))
        if len(matches_list) > 0:
            for match in matches_list['matches']:
                if match['gameId'] not in match_stack and len(match_stack) < nb_match_needed:
                    match_stack.add((sum_id, match['gameId']))
    return match_stack


def extract_timelines(match_id_stack):
    """
    Extract a list of `Matches` objects from riot game API.
    :param nb_match_needed: int
    :return: data_match (list)
    """
    data_timelines = set()
    for match in match_id_stack:
        gameId = match[1]
        game_timeline = api_call.get_timeline(gameId)
        for frame in game_timeline['frames']:
            timestamp = frame.get('timestamp')
            for participant in frame['participantFrames']:
                tpl_timelines_data = (
                    gameId,
                    participant,
                    timestamp
                    )
                # get the column names of the table
                fields_timeline = (str(col).split(".")[-1] for col in Timelines.__table__.columns)
                # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                new_part_entry = Timelines(**dict(zip(fields_timeline, tpl_timelines_data)))
                data_timelines.add(new_part_entry)
    return data_timelines


def extract_events(p_session, match_id_stack):
    """
    Extract a list of matches timelines which contain:
        - A list of frames where each frame is:
        - A dict where the entries are:
        - stats: the list of Stats objects for the

    :return: matches_timeline (list)
    """
    event_id_res = p_session.query(func.max(Events.eventId)).one()
    if event_id_res[0] is None:
        event_id = 0
    else:
        event_id = event_id_res[0]
    # get all match ids
    matches_timeline = list()
    # for all match ids
    for matchid in match_id_stack:
        gameId = matchid[1]
        timeline = api_call.get_timeline(gameId)
        frames = list()
        nb_frame_viewed = 0
        # for each frame of the timeline of the match
        for frame in timeline['frames']:
            dict_data_frame = dict()
            l_stats_frame = list()
            l_events = list()
            l_item_event = list()
            l_assist_ids = list()
            l_kill_event = list()
            l_ward_event = list()
            l_build_event = list()
            l_monster_event = list()
            timestamp = frame['timestamp']
            # stats for each minute
            nb_frame_viewed += 1
            if nb_frame_viewed < len(timeline['frames']):
                for _, value in frame['participantFrames'].items():
                    # get the column names of the table
                    fields_stats = (str(col).split(".")[-1] for col in Stats.__table__.columns)
                    # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                    data_stats = (
                        gameId,
                        value.get('participantId'),
                        timestamp,
                        value.get('level'),
                        value.get('currentGold'),
                        value.get('minionsKilled'),
                        value.get('xp'),
                        value.get('jungleMinionsKilled'),
                        value.get('position').get('x'),
                        value.get('position').get('y')
                    )
                    new_stats_entry = Stats(**dict(zip(fields_stats, data_stats)))
                    l_stats_frame.append(new_stats_entry)
                # event(kill,deaths,assist,ward placed) for each minute and for each jungler
                for events in frame['events']:
                    event_id += 1
                    if 'ITEM' in events['type']:
                        data_event = (
                            event_id,
                            gameId,
                            events.get('participantId'),
                            events.get('type'),
                            events.get('timestamp')
                        )
                        fields_events = (str(col).split(".")[-1] for col in Events.__table__.columns)
                        new_events_entry = Events(**dict(zip(fields_events, data_event)))
                        fields_purchase = (str(col).split(".")[-1] for col in ItemsEvents.__table__.columns)
                        data_purchase = (
                            event_id,
                            events.get('itemId'),
                            events.get('type')
                        )
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_purchase_entry = ItemsEvents(**dict(zip(fields_purchase, data_purchase)))
                        l_item_event.append(new_purchase_entry)
                        l_events.append(new_events_entry)
                    elif events['type'] == 'CHAMPION_KILL':
                        data_event = (
                            event_id,
                            gameId,
                            events.get('killerId'),
                            events.get('type'),
                            events.get('timestamp')
                        )
                        fields_events = (str(col).split(".")[-1] for col in Events.__table__.columns)
                        new_events_entry = Events(**dict(zip(fields_events, data_event)))
                        # we can concatenate the IDs in order to create an ID for the table assist
                        if len(events['assistingParticipantIds']) > 0:
                            for assist in events['assistingParticipantIds']:
                                data_assist = (
                                    event_id,
                                    assist
                                    )
                                fields_assist = (str(col).split(".")[-1] for col in AssistsEvents.__table__.columns)
                                new_assist_entry = AssistsEvents(**dict(zip(fields_assist, data_assist)))
                                l_assist_ids.append(new_assist_entry)
                        kill_data = (
                            event_id,
                            events.get('victimId'),
                            events.get('position').get('x'),
                            events.get('position').get('y')
                        )
                        # get the column names of the table
                        fields_kill = (str(col).split(".")[-1] for col in KillsEvents.__table__.columns)
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_kill_entry = KillsEvents(**dict(zip(fields_kill, kill_data)))
                        l_kill_event.append(new_kill_entry)
                        l_events.append(new_events_entry)
                    elif 'WARD' in events['type']:
                        data_event = (
                            event_id,
                            gameId,
                            utils.getWardParticipant(events),
                            events.get('type'),
                            events.get('timestamp')
                        )
                        fields_events = (str(col).split(".")[-1] for col in Events.__table__.columns)
                        new_events_entry = Events(**dict(zip(fields_events, data_event)))
                        # we can concatenate the IDs in order to create an ID for the table assist
                        ward_data = (
                            event_id,
                            events.get('type'),
                            events.get('wardType'),
                        )
                        # get the column names of the table
                        fields_ward = (str(col).split(".")[-1] for col in WardsEvents.__table__.columns)
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_ward_entry = WardsEvents(**dict(zip(fields_ward, ward_data)))
                        l_ward_event.append(new_ward_entry)
                        l_events.append(new_events_entry)
                    elif 'MONSTER' in events['type']:
                        data_event = (
                            event_id,
                            gameId,
                            events.get('killerId'),
                            events.get('type'),
                            events.get('timestamp')
                        )
                        fields_events = (str(col).split(".")[-1] for col in Events.__table__.columns)
                        new_events_entry = Events(**dict(zip(fields_events, data_event)))
                        # we can concatenate the IDs in order to create an ID for the table assist
                        monster_data = (
                            event_id,
                            events.get('monsterType'),
                            events.get('monsterSubType'),
                            events.get('position').get('x'),
                            events.get('position').get('y')
                        )
                        # get the column names of the table
                        fields_monster = (str(col).split(".")[-1] for col in MonstersEvents.__table__.columns)
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_monster_entry = MonstersEvents(**dict(zip(fields_monster, monster_data)))
                        l_monster_event.append(new_monster_entry)
                        l_events.append(new_events_entry)
                    elif 'BUILDING' in events['type']:
                        data_event = (
                            event_id,
                            gameId,
                            events.get('killerId'),
                            events.get('type'),
                            events.get('timestamp')
                        )
                        fields_events = (str(col).split(".")[-1] for col in Events.__table__.columns)
                        new_events_entry = Events(**dict(zip(fields_events, data_event)))
                        # we can concatenate the IDs in order to create an ID for the table assist
                        build_data = (
                            event_id,
                            events.get('buildingType'),
                            events.get('towerType'),
                            events.get('teamId'),
                            events.get('laneType'),
                            events.get('position').get('x'),
                            events.get('position').get('y')
                        )
                        # get the column names of the table
                        fields_build = (str(col).split(".")[-1] for col in BuildingEvents.__table__.columns)
                        # the dict-zip thing create a mapping between fields and data. This is exploded and used as arg
                        new_build_entry = BuildingEvents(**dict(zip(fields_build, build_data)))
                        l_build_event.append(new_build_entry)
                        l_events.append(new_events_entry)
            dict_data_frame['stats'] = l_stats_frame
            dict_data_frame['build_event'] = l_build_event
            dict_data_frame['item_event'] = l_item_event
            dict_data_frame['events'] = l_events
            dict_data_frame['kill_event'] = l_kill_event
            dict_data_frame['ward_event'] = l_ward_event
            dict_data_frame['monster_event'] = l_monster_event
            dict_data_frame['assist_event'] = l_assist_ids
            frames.append(dict_data_frame)
        matches_timeline.append(frames)
    return matches_timeline

