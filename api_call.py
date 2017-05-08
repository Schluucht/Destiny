import time
import logging
import os
import requests

import settings

stream_handler = logging.StreamHandler()
api_log = logging.getLogger("api_call_logger")
api_log.addHandler(stream_handler)
api_log.setLevel(logging.DEBUG)

d_error_code_msg_s = {
    400: "Bad request",
    401: "Unauthorized",
    403: "Blacklisted or invalid key",
    404: "Game data not found",
    429: "Too many requests",
    500: "Internal server error",
    503: "Service unavailable",
    504: 'Gateway timeout',
}


def do_query(url):
    """
    Makes the api call and eventually handle errors.

    Error handling:
        - 429: Too many requests -> wait then re-try
        - others: -> exit

    :param url: the pre-formatted url for the api
    :return: response.json (dict)
    """
    r = requests.get(url)
    # Code is not 200 if something went wrong

    while r.status_code != 200:
        status_string = "Request status %s in api_call.do_query %s" % (
            r.status_code, d_error_code_msg_s[r.status_code])
        while r.status_code == 429:
            time_sleep = int(r.headers["Retry-After"]) + 2
            status_string += " -> Retrying in %s seconds." % time_sleep
            api_log.debug(status_string)
            time.sleep(time_sleep)
            # continue loop with new request
            r = requests.get(url)
        # if status_code is still not 200 after the 429 loop
        if r.status_code != 200:
            status_string += ". url: %s -> Exiting." % url
            api_log.error(status_string)
            exit()
    api_log.debug("Request status %s in api_call.do_query -> Succeed." % r.status_code)
    return r.json()


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
