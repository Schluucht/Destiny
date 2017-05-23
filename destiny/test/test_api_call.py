import time
import requests
import destiny.settings as settings
from destiny.main.destinyexception import DestinyApiCallException
from destiny.main.destinylogger import api_log


def test_do_query():
    """
    Makes the api call and eventually handle errors.

    Error handling:
        - 429: Too many requests -> wait then re-try
        - others: -> exit

    :param url: the pre-formatted url for the api
    :return: response.json (dict)
    """
    urls = {
        "timelines":
            "https://euw1.api.riotgames.com//lol/match/v3/timelines/by-match/3181575441?api_key=RGAPI-6d8d1f8b-2f06-40f0-8177-c6ff597533d7",
        "matches":
            "https://euw1.api.riotgames.com//lol/match/v3/matches/3181575441?api_key=RGAPI-6d8d1f8b-2f06-40f0-8177-c6ff597533d7"
    }


def get_challenger():
    """
    API documentation: https://developer.riotgames.com/api-methods/#league-v3/GET_getChallengerLeague

    :return:
    """
    url = settings.REGION + 'lol/league/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=' + settings.API_KEY
    return do_query(url)


def get_league_by_summoner(id_summoner):
    """
    API documentation: https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguesForSummoner

    :param id_summoner:
    :return:
    """
    url = settings.REGION + '/lol/league/v3/leagues/by-summoner/'+str(id_summoner)+'?api_key='+settings.API_KEY
    return do_query(url)


def get_acount_id(id_summoner):
    """
    API documentation: https://developer.riotgames.com/api-methods/#summoner-v3/GET_getBySummonerId

    :param id_summoner:
    :return:
    """
    url = settings.REGION + '/lol/summoner/v3/summoners/'+str(id_summoner)+'?api_key='+settings.API_KEY
    return do_query(url)


def get_matchlist(id_account):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getRecentMatchlist

    :param id_account:
    :return:
    """
    url = settings.REGION + '/lol/match/v3/matchlists/by-account/'+str(id_account)+'/recent?api_key='+settings.API_KEY
    return do_query(url)


def get_match(id_match):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getMatch

    :param id_match:
    :return:
    """
    url = settings.REGION + '/lol/match/v3/matches/'+str(id_match)+'?api_key='+settings.API_KEY
    return do_query(url)


def get_timeline(id_match):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchTimeline

    :param id_match:
    :return:
    """
    url = settings.REGION + '/lol/match/v3/timelines/by-match/'+str(id_match)+'?api_key='+settings.API_KEY
    return do_query(url)


def get_champion():
    """
    API documentation: https://developer.riotgames.com/api-methods/#static-data-v3/GET_getChampionList

    :return:
    """
    url = settings.REGION + '/lol/static-data/v3/champions?api_key=' + settings.API_KEY
    return do_query(url)
