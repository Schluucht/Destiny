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
        p_session.bulk_save_objects(p_data)
        p_session.commit()

    except IntegrityError as err:
        db_log.error(err)
        p_session.rollback()
