def load_summoners(cnx, data):
    cursor = cnx.cursor()
    add_player = ("INSERT IGNORE INTO players (summoner_id, account_id, tier, last_refresh) VALUES (%s, %s, %s, %s)")
    for summoner in data:
        data_player = (summoner['summoner_id'],
                       summoner['account_id'],
                       summoner['tier'],
                       summoner['last_refresh'])
        cursor.execute(add_player,data_player)
        cnx.commit()
    cursor.close()

def load_matches(cnx, data):
    cursor = cnx.cursor()
    add_match = ("INSERT IGNORE INTO matches (gameId, platformId, season, timestamp) VALUES (%s, %s, %s, %s)")
    for match in data:
        data_match = (match['match_id'],
                      match['platform_id'],
                      int(match['season_id']),
                      int(match['game_duration']))
        cursor.execute(add_match,data_match)
        cnx.commit()
    cursor.close()

def load_timelines(cnx, data):
    cursor = cnx.cursor()