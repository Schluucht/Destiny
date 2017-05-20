import mysql.connector
import logging
import destiny.settings as settings

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

db_log = logging.getLogger("db_logger")
db_log.addHandler(stream_handler)
db_log.setLevel(logging.DEBUG)


def clean_database(cnx):
    """
    Fully Truncate all the tables of the database.

    Ask for confirmation before truncate.
    :param cnx: Connexion object
    :return: None
    """
    confirmation = input("Destiny is about to drop the whole database. Do you agree? y/N").strip()
    if confirmation != 'y':
        db_log.info("DB won't be empty.")
        return

    cursor = cnx.cursor()
    query = ("SHOW TABLES;")
    cursor.execute(query)
    tables = list(cursor)

    for table in tables:
        table_name = table[0]
        cursor.execute("TRUNCATE TABLE %s" % table_name)
        db_log.info("%s table truncated." % table_name)

    cursor = cnx.cursor()
    query = ("SHOW TABLES;")
    cursor.execute(query)


def get_connection_db(*args, **kwargs):
    """
    Create proper connexion to database.

    :param cnx: Connexion object
    :return: None
    """
    try:
        cnx = mysql.connector.connect(*args, **kwargs)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            db_log.error("Something is wrong with your user name or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            db_log.error("Database does not exist")
        else:
            db_log.error(err)
        sys.exit(1)


def close_cnx(cnx):
    """
    Close database connexion.

    :param cnx: Connexion object
    :return: None
    """
    cnx.close()

