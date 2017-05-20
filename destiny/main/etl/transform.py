import destiny.main.api_call as api_call
from destiny.utils import deprecated


@deprecated
def get_participant_champ(match):
    """
    extract from match data champion ID associate to participant ID.

    Ask for confirmation before truncate.
    :param match: a dictionnary
    :return: a dictionnary
    """
    participants = {0 : 'Unknown'}
    blue_side = construct_role_list(match,'BLUE')
    red_side = construct_role_list(match,'RED')
    if role_checker(blue_side) and role_checker(red_side):
        for part in match['participants']:
            participants[part['participantId']] = CHAMPIONS[str(part['championId'])]
    return participants


@deprecated
def get_champion_list():
    """
    extract champions list ID.

    :return: a dictionnary
    """
    champion_data = api_call.get_champion()
    champions = dict()
    for champion in champion_data['data'].values():
        champions[str(champion['id'])] = champion['name']
    return champions


@deprecated
def role_checker(roles):
    """
    Check if all roles are present in roles.

    :param roles: a set
    :return: a boolean
    """
    set_supported_roles = {'TOP SOLO','MIDDLE SOLO','BOTTOM DUO_SUPPORT','BOTTOM DUO_CARRY','JUNGLE NONE'}
    if len(set(roles).difference(set_supported_roles)) != 0:
        return False
    else:
       return True


@deprecated
def construct_role_list(data,side):
    """
    Create set of all roles detected in data but only for one side (blue or red).

    :param match: a dictionnary
    :param side: a string
    :return: a set
    """
    roles = set()
    if side == 'RED':
        for i in range (0,5):
            role = data['participants'][i]['timeline']['lane'] + ' ' + data['participants'][i]['timeline']['role']
            roles.add(role)
    elif side == 'BLUE':
        for i in range (5,10):
            role = data['participants'][i]['timeline']['lane'] + ' ' + data['participants'][i]['timeline']['role']
            roles.add(role)
    return roles
