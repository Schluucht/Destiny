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
        data_to_print = 3
        s_data = "["
        s_data += ",".join(str(d) for d in p_data[:data_to_print])
        if len(p_data) > data_to_print:
            s_data += ", ..."
        s_data += "]"
        db_log.debug("Adding data {} to session".format(s_data))
        p_session.add_all(p_data)
        db_log.debug("Commiting")
        p_session.commit()
    except IntegrityError as IE:
        db_log.error(IE)
        raise IE


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