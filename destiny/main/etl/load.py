def load_summoners(cnx, data):
    """
    Insert summoners informations into the corresponding database table.

    :param cnx: Connexion object
    :param data: Dictionnary
    :return: None
    """
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
    """
    Insert matches informations into the corresponding database table.

    :param cnx: Connexion object
    :param data: Dictionnary
    :return: None
    """
    cursor = cnx.cursor()
    add_match = ("INSERT IGNORE INTO matches (game_id, platform_id, season, timestamp) VALUES (%s, %s, %s, %s)")
    for match in data:
        data_match = (match['match_id'],
                      match['platform_id'],
                      int(match['season_id']),
                      int(match['game_duration']))
        cursor.execute(add_match,data_match)
        cnx.commit()
    cursor.close()


def load_timelines(cnx, data):
    """
    Insert timelines informations into the corresponding database table.

    :param cnx: Connexion object
    :param data: Dictionnary
    :return: None
    """
    cursor = cnx.cursor()
    for timelines in data:
        game_id = timelines['game_id']
        for timeline in timelines['frames']:
            timestamp = timeline['timestamp']
            for stat in timeline['stats']:
                add_stats = ("INSERT IGNORE INTO stats (game_id, timestamp, participant_id, level, current_gold, minions_killed, xp, jungle_minions_killed, x ,y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                participant_id = stat['participant_id']
                level = stat['level']
                current_gold = stat['current_gold']
                minions_killed = stat['minions_killed']
                xp = stat['xp']
                jungle_minions_killed = stat['jungle_minions_killed']
                x = stat['position_x']
                y = stat['position_y']
                data_stats = (int(game_id),
                              int(timestamp),
                              int(participant_id),
                              int(level),
                              int(current_gold),
                              int(minions_killed),
                              int(xp),
                              int(jungle_minions_killed),
                              int(x),
                              int(y))
                cursor.execute(add_stats, data_stats)
            for event in timeline['item_event']:
                add_purchase = ("INSERT IGNORE INTO itemEvent (game_id, item_id, timestamp, participant) VALUES (%s, %s, %s, %s)")
                data_purchase = (game_id, event['item_id'], timestamp, event['participant_id'])
                cursor.execute(add_purchase, data_purchase)
            #todo manage assists
            for event in timeline['kill_event']:
                add_kill = ("INSERT IGNORE INTO killEvent (game_id, killer, victim, timestamp, x, y) VALUES (%s, %s, %s, %s, %s, %s)")
                killer = event['killer']
                victim = event['victim']
                x = event['position_x']
                y = stat['position_y']
                data_kill = (game_id, killer, victim, timestamp, x, y)
                cursor.execute(add_kill, data_kill)
        cnx.commit()
    cursor.close()