import os
import logging

try:
    from yaml import CLoader as Loader, CDumper as Dumper, load
except ImportError:
    from yaml import Loader, Dumper, load

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

settings_log = logging.getLogger("settings_logger")
settings_log.addHandler(stream_handler)
settings_log.setLevel(logging.DEBUG)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, "config.yml")) as f:
    file_dict = load(f)
    API_KEY = file_dict['api-key'].strip()
    settings_log.debug("API KEY: %s" % API_KEY)
    DB_HOST = file_dict['mysql_database']['host'].strip()
    DB_PORT = file_dict['mysql_database']['port']
    DB_NAME = file_dict['mysql_database']['name'].strip()
    DB_USER = file_dict['mysql_database']['user'].strip()
    DB_PASSWORD = file_dict['mysql_database']['password'].strip()

REGION = 'https://euw1.api.riotgames.com/'



