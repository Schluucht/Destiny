from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

import destiny.settings as settings
from destiny.main.destinylogger import db_log

printed_connection_string = '{0}{1}://{2}:***@{4}:{5}/{6}'
connection_string = '{0}{1}://{2}:{3}@{4}:{5}/{6}'

tpl_settings = (settings.DB_DIALECT,
                      "+" + settings.DB_DRIVER if settings.DB_DRIVER is not "" else settings.DB_DRIVER,
                      settings.DB_USER,
                      settings.DB_PASSWORD,
                      settings.DB_HOST,
                      settings.DB_PORT,
                      settings.DB_NAME)


db_log.debug("Connection string: {}".format(printed_connection_string).format(*tpl_settings))

engine = create_engine(connection_string.format(*tpl_settings))
Session = sessionmaker(bind=engine)()
