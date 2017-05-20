import logging

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

import destiny.settings as settings
from destiny.utils import stream_handler


db_log = logging.getLogger("db_logger")
db_log.addHandler(stream_handler)
db_log.setLevel(logging.DEBUG)

connection_string = ('%s%s://%s:%s@%s:%s/%s' %
                     (settings.DB_DIALECT,
                      "+" + settings.DB_DRIVER if settings.DB_DRIVER is not "" else settings.DB_DRIVER,
                      settings.DB_USER,
                      settings.DB_PASSWORD,
                      settings.DB_HOST,
                      settings.DB_PORT,
                      settings.DB_NAME))
db_log.debug("Connection string: %s" % connection_string)

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)()
