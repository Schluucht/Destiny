import logging

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

settings_log = logging.getLogger("settings_logger")
settings_log.addHandler(stream_handler)
settings_log.setLevel(logging.DEBUG)

db_log = logging.getLogger("db_logger")
db_log.addHandler(stream_handler)
db_log.setLevel(logging.DEBUG)

api_log = logging.getLogger("api_call_logger")
api_log.addHandler(stream_handler)
api_log.setLevel(logging.DEBUG)

ext_log = logging.getLogger("extract_logger")
ext_log.addHandler(stream_handler)
ext_log.setLevel(logging.DEBUG)
