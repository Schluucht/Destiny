from sqlalchemy.ext.declarative import declarative_base

from destiny.main.bdd.connexion import db_log

Base = declarative_base()


def clean_database(p_engine, p_force=False):
    """
    Drop all tables of the database.

    :param p_engine: The current used engine.
    :type p_engine: sqlalchemy.engine.Engine
    :param p_force: Don't ask for confirmation. (default: False)
    :type p_force: Boolean
    :return:
    """
    if not p_force:
        confirmation = input("Destiny is about to drop the whole database. Do you agree? y/N").strip()
        if confirmation != 'y':
            db_log.info("DB won't be empty.")
            return
    db_log.debug("Start droping tables with engine %s." % p_engine)
    Base.metadata.drop_all(p_engine)
    db_log.info("Tables droped")


def create_tables(p_engine):
    db_log.debug("Start creating tables with engine %s." % p_engine)
    Base.metadata.create_all(p_engine)
    db_log.info("Tables created")