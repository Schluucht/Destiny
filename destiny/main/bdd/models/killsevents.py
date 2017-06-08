from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class KillsEvents(Base):
    __tablename__ = 'killsEvents'

    eventId = Column(BigInteger, primary_key=True)
    victimId = Column(SmallInteger)
    x = Column(SmallInteger)
    y = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
