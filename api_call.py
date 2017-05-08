import time
import os
import requests

from yaml import load

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY = ''
with open(os.path.join(ROOT_DIR, "config.yml")) as f:
    API_KEY = load(f)['api-key'].strip()
    print "API KEY: %s" % API_KEY

REGION = 'https://euw1.api.riotgames.com/'

#https://developer.riotgames.com/api-methods/#league-v3/GET_getChallengerLeague
def get_challenger():
    url = REGION + 'lol/league/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        time.sleep(180)
        get_challenger()
    else:
        time.sleep(1)
    return request.json()

#https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguesForSummoner
def get_league_by_summoner(id_summoner):
    url = REGION + '/lol/league/v3/leagues/by-summoner/'+str(id_summoner)+'?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_league_by_summoner(id_summoner)
    else:
        time.sleep(1)
    return request.json()

def get_acount_id(id_summoner):
    url = REGION + '/lol/summoner/v3/summoners/'+str(id_summoner)+'?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_acount_id(id_summoner)
    else:
        time.sleep(1)
    return request.json()

def get_matchlist(id_account):
    url = REGION + '/lol/match/v3/matchlists/by-account/'+str(id_account)+'/recent?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_matchlist(id_account)
    else:
        time.sleep(1)
    return request.json()

def get_match(id_match):
    url = REGION + '/lol/match/v3/matches/'+str(id_match)+'?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_match(id_match)
    else:
        time.sleep(1)
    return request.json()

def get_timeline(id_match):
    url = REGION + '/lol/match/v3/timelines/by-match/'+str(id_match)+'?api_key='+API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_timeline(id_match)
    else:
        time.sleep(1)
    return request.json()

def get_champion():
    url = REGION + '/lol/static-data/v3/champions?api_key=' + API_KEY
    request = requests.get(url)
    if request.status_code == 429:
        print "error 429"
        time.sleep(180)
        get_champion()
    else:
        time.sleep(1)
    return request.json()
