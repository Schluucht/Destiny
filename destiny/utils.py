import warnings
import logging


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                       category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)

    return new_func


def rep_model(self):
    """
    Dynamic fancy string generation for an object attributes.

    :param self: any object
    :return: the string representation of the attributes of this object
    """
    dict_obj_att = self.__dict__['_sa_instance_state'].__dict__['class_'].__dict__
    # gather the attributes of the objects in a dict
    s = "<%s(" % self.__class__.__name__
    l_str_attributes = []
    for var, value in dict_obj_att.items():
        if not var.startswith("_"):
            l_str_attributes.append("%s='%s'" % (var, eval("self." + str(value).split('.')[-1])))
    s += ", ".join(l_str_attributes)
    s += ")>"
    return s


def get_event_type(event):
    if 'ITEM' in event:
        return 'ITEM'
    elif 'CHAMPION_KILL' in event:
        return 'CHAMPION'
    elif 'ELITE_MONSTER_KILL' in event:
        return 'MONSTER_KILL'
    elif 'BUILDING_KILL' in event:
        return 'BUILDING'
    elif 'WARD' in event:
        return 'WARD'
    else:
        return None


def getWardParticipant(data):
    if 'creatorId' in data:
        return data.get('creatorId')
    else :
        return data.get('killerId')
