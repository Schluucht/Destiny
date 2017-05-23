import destiny.settings as settings
from destiny.main.api_call import do_query, get_challenger, get_league_by_summoner, get_acount_id, get_matchlist, \
    get_match, get_timeline, get_champion
import pytest

from destiny.main.destinyexception import DestinyApiCallException


@pytest.fixture
def id_summoner():
    return 56947948


@pytest.fixture
def id_account():
    return 209493252


@pytest.fixture
def id_match():
    return 3181575441


def test_do_query():
    """
    Tests `api_call.do_query` function.

    Use the function against prepared urls and check that the returned results are not empty.
    """
    urls = {
        "timelines":
            settings.REGION + "/lol/match/v3/timelines/by-match/3181575441?api_key=" + settings.API_KEY,
        "matches":
            settings.REGION + "/lol/match/v3/matches/3181575441?api_key=" + settings.API_KEY,
        "summoners":
            settings.REGION + "/lol/summoner/v3/summoners/56947948?api_key=" + settings.API_KEY,
        "matchlist":
            settings.REGION + "/lol/match/v3/matchlists/by-account/209493252/recent?api_key=" + settings.API_KEY
    }
    for _type, url in urls.items():
        assert len(do_query(url)) > 0

    with pytest.raises(DestinyApiCallException) as DE401:
        url_401 = "https://euw1.api.riotgames.com//lol/unauthorized/"
        do_query(url_401)
    assert DE401.value.err_code == 401

    with pytest.raises(DestinyApiCallException) as DE404:
        url_404 = "https://euw1.api.riotgames.com//lol/match/v3/matches/31815751235441?api_key=" + settings.API_KEY
        do_query(url_404)
    assert DE404.value.err_code == 404

    with pytest.raises(DestinyApiCallException) as DE403:
        url_403 = "https://euw1.api.riotgames.com//lol/match/v3/matches/31815751235441?api_key=invalid"
        do_query(url_403)
    assert DE403.value.err_code == 403


def test_get_challenger():
    """
    Tests `api_call.get_challenger()` function.

    Tests if the returned dict contains something.
    :return:
    """
    assert len(get_challenger()) > 0


def test_get_league_by_summoner(id_summoner):
    """
    API documentation: https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguesForSummoner

    :param id_summoner:
    :return:
    """
    assert len(get_league_by_summoner(id_summoner)) > 0


def test_get_acount_id(id_summoner):
    """
    API documentation: https://developer.riotgames.com/api-methods/#summoner-v3/GET_getBySummonerId

    :param id_summoner:
    :return:
    """
    assert len(get_acount_id(id_summoner)) > 0


def test_get_matchlist(id_account):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getRecentMatchlist

    :param id_account:
    :return:
    """
    assert len(get_matchlist(id_account)) > 0


def test_get_match(id_match):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getMatch

    :param id_match:
    :return:
    """
    assert len(get_match(id_match)) > 0


def test_get_timeline(id_match):
    """
    API documentation: https://developer.riotgames.com/api-methods/#match-v3/GET_getMatchTimeline

    :param id_match:
    :return:
    """
    assert len(get_timeline(id_match)) > 0


def test_get_champion():
    """
    API documentation: https://developer.riotgames.com/api-methods/#static-data-v3/GET_getChampionList

    :return:
    """
    assert len(get_champion()) > 0
