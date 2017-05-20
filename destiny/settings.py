import os
import logging
from destiny.utils import stream_handler
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load
except ImportError:
    from yaml import Loader, Dumper, load


settings_log = logging.getLogger("settings_logger")
settings_log.addHandler(stream_handler)
settings_log.setLevel(logging.DEBUG)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, "../config.yaml")) as f:
    file_dict = load(f)
    API_KEY = file_dict['api-key'].strip()
    settings_log.debug("API KEY: %s" % API_KEY)
    DB_DIALECT = file_dict['mysql_database']['dialect'].strip()
    DB_DRIVER = file_dict['mysql_database']['driver'].strip()
    DB_HOST = file_dict['mysql_database']['host'].strip()
    DB_PORT = file_dict['mysql_database']['port']
    DB_NAME = file_dict['mysql_database']['name'].strip()
    DB_USER = file_dict['mysql_database']['user'].strip()
    DB_PASSWORD = file_dict['mysql_database']['password'].strip()
    NB_PLAYERS_NEEDED = int(file_dict['data_to_extract']['nb_players_needed'])
    NB_MATCHES_NEEDED = int(file_dict['data_to_extract']['nb_matches_needed'])
    TYPE_OF_GAME_NEEDED = int(file_dict['data_to_extract']['type_of_game_needed'])

REGION = 'https://euw1.api.riotgames.com/'



