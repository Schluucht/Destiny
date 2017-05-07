import requests
import time
from pymongo import MongoClient

api_key =  #to do extractFrom file
region = 'https://euw1.api.riotgames.com/'

#https://developer.riotgames.com/api-methods/#league-v3/GET_getChallengerLeague
def get_challenger():
	url = region + 'lol/league/v3/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		time.sleep(180)
		get_challenger()
	else:
		time.sleep(1)
	return r.json()

#https://developer.riotgames.com/api-methods/#league-v3/GET_getAllLeaguesForSummoner
def get_league_by_summoner(id_summoner):
	url = region + '/lol/league/v3/leagues/by-summoner/'+str(id_summoner)+'?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		print "error 429"
		time.sleep(180)
		get_league_by_summoner(id_summoner)
	else:
		time.sleep(1)
	return r.json()

def get_acount_id(id_summoner):
	url = region + '/lol/summoner/v3/summoners/'+str(id_summoner)+'?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		print "error 429"
		time.sleep(180)
		get_acount_id(id_summoner)
	else:
		time.sleep(1)
	return r.json()

def get_matchlist(id_account):
	url = region + '/lol/match/v3/matchlists/by-account/'+str(id_account)+'/recent?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		print "error 429"
		time.sleep(180)
		get_matchlist(id_account)
	else:
		time.sleep(1)
	return r.json()

def get_match(id_match):
	url = region + '/lol/match/v3/matches/'+str(id_match)+'?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		print "error 429"
		time.sleep(180)
		get_matchlist(id_summoner)
	else:
		time.sleep(1)
	return r.json()

def get_timeline(id_match):
	url = region + '/lol/match/v3/timelines/by-match/'+str(id_match)+'?api_key='+api_key
	r = requests.get(url)
	if r.status_code == 429:
		print "error 429"
		time.sleep(180)
		get_matchlist(id_summoner)
	else:
		time.sleep(1)
	return r.json()