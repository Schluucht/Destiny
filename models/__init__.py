from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# models imports
# import participant
# import matches
# import players


def rep_model(self):
    """
    Dynamic string generation for an object attributes.

    :param self: any object
    :return: the string representation of the attributes of this object
    """
    dict_obj_att = self.__dict__['_sa_instance_state'].__dict__['class_'].__dict__
    # gather the attributes of the objects in a dict
    s = "<%s(" % self.__class__.__name__
    s += ", ".join(["%s='%s'" % (key, eval("self." + str(value).split('.')[-1]))
                    for key, value in dict_obj_att.iteritems()
                    if not key.startswith("_")])
    s += ")>"
    return s
