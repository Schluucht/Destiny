from sqlalchemy.exc import IntegrityError

from destiny.main.destinylogger import db_log

def load_data(p_session, p_data):
    """
    Insert the list of models instances in the current session then commit.

    :param p_session: Session object.
    :param p_data: List of models instances.
    :return: None
    """
    try:
        p_session.add_all(p_data)
        p_session.commit()
    except IntegrityError as err:
        db_log.error(err)
        p_session.rollback()


def load_timelines(p_session, data):
    """
    Insert timelines informations into the corresponding database table.

    :param p_session: Connexion object
    :param data: Dictionnary
    :return: None
    """
    for timeline in data:
        for frame in timeline:
            load_data(p_session, frame['stats'])
            load_data(p_session, frame['item_event'])
            load_data(p_session, frame['kill_event'])
            load_data(p_session, frame['build_event'])
            load_data(p_session, frame['ward_event'])
            load_data(p_session, frame['events'])
            load_data(p_session, frame['monster_event'])
            load_data(p_session, frame['assist_event'])