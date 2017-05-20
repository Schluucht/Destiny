from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
