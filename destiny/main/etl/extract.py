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

def init_summoner_stack(p_session):
    # initialize variable
    summoners_stack = set()
    # initialize summoner_stack with summoner id known
    random_summoner = extract_master_sum_id()
    summoners_stack.add(random_summoner)  # need to be configurable

    if len(summoners_stack) == 0:
        one_summoner = p_session.query(Players.summonerId).one()
        summoners_stack.add(one_summoner)

    return summoners_stack

def extract_sum_id_from_league(league, summoners_stack, nb_sum_needed):
    data_summoner = set()
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
            # todo make it dynamic with the dictzip thing
            data_summoner.add(Players(summonerId=summoner_id, accountId=account_id, tier=tier, lastRefresh=last_refresh))
    return data_summoner

def extract_summoners(p_session, nb_sum_needed):
    """
    Extract a list of `Players` objects from riot games API.

    :param p_session: Connexion object
    :param nb_sum_needed: int
    :return: data_summoner (list)
    """
    # initialize variable
    summoners_stack = init_summoner_stack(p_session)
    data_summoner = set()

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
            sum_id_to_insert = extract_sum_id_from_league(league, summoners_stack, nb_sum_needed)
            data_summoner = data_summoner | sum_id_to_insert

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
        some_match = Matches(
            gameId=match.get('gameId'),
            platformId=match.get('platformId'),
            season=match.get('seasonId'),
            gameVersion=match.get('gameVersion'),
            timestamp=match.get('gameDuration') 
        )
        data_match.add(some_match)
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
            some_team_stats = TeamStats(
                gameId=gameId,
                teamId=team.get('teamId'),
                firstDragon=team.get('firstDragon'),
                firstInhibitor=team.get('firstInhibitor'),
                baronKills=team.get('baronKills'),
                firstRiftHerald=team.get('firstRiftHerald'),
                firstBaron=team.get('firstBaron'),
                riftHeraldKills=team.get('riftHeraldKills'),
                firstBlood=team.get('firstBlood'),
                firstTower=team.get('firstTower'),
                inhibitorKills=team.get('inhibitorKills'),
                towerKills=team.get('towerKills'),
                win=team.get('win'),
                dragonKills=team.get('dragonKills')
            )
            data_team_stats.add(some_team_stats)
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
                some_ban = Bans(
                    gameId=gameId,
                    teamId=team.get('teamId'),
                    pickTurn=ban.get('pickTurn'),
                    championId=ban.get('championId'),
                )
                data_bans.add(some_ban)

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
            some_participant = Participants(
                gameId=gameId,
                participantId=participant.get('participantId'),
                teamId=participant.get('teamId'),
                highestAchievedSeasonTier=participant.get('highestAchievedSeasonTier'),
                championId=participant.get('championId'),
                spell1Id=participant.get('spell1Id'),
                spell2Id=participant.get('spell2Id')
            )
            data_match.add(some_participant)
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
            some_participant = ParticipantStats(
                gameId=gameId,
                participantId=participant.get('stats').get('participantId'),
                physicalDamageDealt=participant.get('stats').get('physicalDamageDealt'),
                neutralMinionsKilledTeamJungle=participant.get('stats').get('neutralMinionsKilledTeamJungle'),
                magicDamageDealt=participant.get('stats').get('magicDamageDealt'),
                totalPlayerScore=participant.get('stats').get('totalPlayerScore'),
                deaths=participant.get('stats').get('deaths'),
                win=participant.get('stats').get('win'),
                neutralMinionsKilledEnemyJungle=participant.get('stats').get('neutralMinionsKilledEnemyJungle'),
                largestCriticalStrike=participant.get('stats').get('largestCriticalStrike'),
                totalDamageDealt=participant.get('stats').get('totalDamageDealt'),
                magicDamageDealtToChampions=participant.get('stats').get('magicDamageDealtToChampions'),
                visionWardsBoughtInGame=participant.get('stats').get('visionWardsBoughtInGame'),
                damageDealtToObjectives=participant.get('stats').get('damageDealtToObjectives'),
                largestKillingSpree=participant.get('stats').get('largestKillingSpree'),
                item1=participant.get('stats').get('item1'),
                quadraKills=participant.get('stats').get('quadraKills'),
                totalTimeCrowdControlDealt=participant.get('stats').get('totalTimeCrowdControlDealt'),
                longestTimeSpentLiving=participant.get('stats').get('longestTimeSpentLiving'),
                wardsKilled=participant.get('stats').get('wardsKilled'),
                firstTowerAssist=participant.get('stats').get('firstTowerAssist'),
                firstTowerKill=participant.get('stats').get('firstTowerKill'),
                item2=participant.get('stats').get('item2'),
                item3=participant.get('stats').get('item3'),
                item0=participant.get('stats').get('item0'),
                firstBloodAssist=participant.get('stats').get('firstBloodAssist'),
                visionScore=participant.get('stats').get('visionScore'),
                wardsPlaced=participant.get('stats').get('wardsPlaced'),
                item4=participant.get('stats').get('item4'),
                item5=participant.get('stats').get('item5'),
                item6=participant.get('stats').get('item6'),
                turretKills=participant.get('stats').get('turretKills'),
                tripleKills=participant.get('stats').get('tripleKills'),
                damageSelfMitigated=participant.get('stats').get('damageSelfMitigated'),
                champLevel=participant.get('stats').get('champLevel'),
                firstInhibitorKill=participant.get('stats').get('firstInhibitorKill'),
                goldEarned=participant.get('stats').get('goldEarned'),
                magicalDamageTaken=participant.get('stats').get('magicalDamageTaken'),
                kills=participant.get('stats').get('kills'),
                doubleKills=participant.get('stats').get('doubleKills'),
                trueDamageTaken=participant.get('stats').get('trueDamageTaken'),
                firstInhibitorAssist=participant.get('stats').get('firstInhibitorAssist'),
                assists=participant.get('stats').get('assists'),
                unrealKills=participant.get('stats').get('unrealKills'),
                neutralMinionsKilled=participant.get('stats').get('neutralMinionsKilled'),
                objectivePlayerScore=participant.get('stats').get('objectivePlayerScore'),
                combatPlayerScore=participant.get('stats').get('combatPlayerScore'),
                damageDealtToTurrets=participant.get('stats').get('damageDealtToTurrets'),
                physicalDamageDealtToChampions=participant.get('stats').get('physicalDamageDealtToChampions'),
                goldSpent=participant.get('stats').get('goldSpent'),
                trueDamageDealt=participant.get('stats').get('trueDamageDealt'),
                trueDamageDealtToChampions=participant.get('stats').get('trueDamageDealtToChampions'),
                pentaKills=participant.get('stats').get('pentaKills'),
                totalHeal=participant.get('stats').get('totalHeal'),
                totalMinionsKilled=participant.get('stats').get('totalMinionsKilled'),
                firstBloodKill=participant.get('stats').get('firstBloodKill'),
                largestMultiKill=participant.get('stats').get('largestMultiKill'),
                sightWardsBoughtInGame=participant.get('stats').get('sightWardsBoughtInGame'),
                totalDamageDealtToChampions=participant.get('stats').get('totalDamageDealtToChampions'),
                totalUnitsHealed=participant.get('stats').get('totalUnitsHealed'),
                inhibitorKills=participant.get('stats').get('inhibitorKills'),
                totalScoreRank=participant.get('stats').get('totalScoreRank'),
                totalDamageTaken=participant.get('stats').get('totalDamageTaken'),
                killingSprees=participant.get('stats').get('killingSprees'),
                timeCCingOthers=participant.get('stats').get('timeCCingOthers'),
                physicalDamageTaken=participant.get('stats').get('physicalDamageTaken')
            )
            data_participant.add(some_participant)
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
        some_list_matches = ListMatches(summonerId=match[0], gameId=matchid)
        data_match.add(some_list_matches)
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
                some_timelines_data = Timelines(
                    gameId=gameId,
                    participantId=participant,
                    timestamp=timestamp
                    )
                data_timelines.add(some_timelines_data)
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
                    some_stats = Stats(
                        gameId=gameId,
                        participantId=value.get('participantId'),
                        timestamp=timestamp,
                        level=value.get('level'),
                        currentGold=value.get('currentGold'),
                        minionsKilled=value.get('minionsKilled'),
                        xp=value.get('xp'),
                        jungleMinionsKilled=value.get('jungleMinionsKilled'),
                        x=value.get('position').get('x'),
                        y=value.get('position').get('y')
                    )
                    l_stats_frame.append(some_stats)
                # event(kill,deaths,assist,ward placed) for each minute and for each jungler
                for events in frame['events']:
                    event_id += 1
                    if 'ITEM' in events['type']:
                        some_event = Events(
                            eventId=event_id,
                            gameId=gameId,
                            participantId=events.get('participantId'),
                            type_event=events.get('type'),
                            timestamp=events.get('timestamp')
                        )
                        some_purchase = ItemsEvents(
                            eventId=event_id,
                            itemId=events.get('itemId'),
                            eventType=events.get('type')
                        )
                        l_item_event.append(some_purchase)
                        l_events.append(some_event)
                    elif events['type'] == 'CHAMPION_KILL':
                        some_event = Events(
                            eventId=event_id,
                            gameId=gameId,
                            participantId=events.get('killerId'),
                            type_event=events.get('type'),
                            timestamp=events.get('timestamp')
                        )
                        if len(events['assistingParticipantIds']) > 0:
                            for assist in events['assistingParticipantIds']:
                                some_assist = AssistsEvents(
                                    eventId=event_id,
                                    participantId=assist
                                    )
                                l_assist_ids.append(some_assist)
                        some_kill_data = KillsEvents(
                            eventId=event_id,
                            victimId=events.get('victimId'),
                            x=events.get('position').get('x'),
                            y=events.get('position').get('y')
                        )
                        l_kill_event.append(some_kill_data)
                        l_events.append(some_event)
                    elif 'WARD' in events['type']:
                        some_event = Events(
                            eventId=event_id,
                            gameId=gameId,
                            participantId=utils.getWardParticipant(events),
                            type_event=events.get('type'),
                            timestamp=events.get('timestamp')
                        )
                        some_ward = WardsEvents(
                            eventId=event_id,
                            eventType=events.get('type'),
                            wardType=events.get('wardType'),
                        )
                        l_ward_event.append(some_ward)
                        l_events.append(some_event)
                    elif 'MONSTER' in events['type']:
                        some_event = Events(
                            eventId=event_id,
                            gameId=gameId,
                            participantId=events.get('killerId'),
                            type_event=events.get('type'),
                            timestamp=events.get('timestamp')
                        )
                        monster_data = MonstersEvents(
                            eventId=event_id,
                            monsterType=events.get('monsterType'),
                            monsterSubType=events.get('monsterSubType'),
                            x=events.get('position').get('x'),
                            y=events.get('position').get('y')
                        )
                        l_monster_event.append(monster_data)
                        l_events.append(some_event)
                    elif 'BUILDING' in events['type']:
                        some_event = Events(
                            eventId=event_id,
                            gameId=gameId,
                            participantId=events.get('killerId'),
                            type_event=events.get('type'),
                            timestamp=events.get('timestamp')
                        )
                        build_data = BuildingEvents(
                            eventId=event_id,
                            buildingType=events.get('buildingType'),
                            towerType=events.get('towerType'),
                            teamId=events.get('teamId'),
                            laneType=events.get('laneType'),
                            x=events.get('position').get('x'),
                            y=events.get('position').get('y')
                        )
                        l_build_event.append(build_data)
                        l_events.append(some_event)
            matches_timeline += l_stats_frame \
                              + l_build_event \
                              + l_item_event \
                              + l_events \
                              + l_kill_event \
                              + l_ward_event \
                              + l_monster_event \
                              + l_assist_ids \

    return matches_timeline

