def load_data(p_session, p_data):
    """
    Insert the list of models instances in the current session then commit.

    :param p_session: Session object.
    :param p_data: List of models instances.
    :return: None
    """
    p_session.add_all(p_data)
    p_session.commit()


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