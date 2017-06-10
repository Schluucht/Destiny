from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Events(Base):
    __tablename__ = 'events'
    eventId = Column(BigInteger, autoincrement=True, primary_key=True)
    gameId = Column(BigInteger)
    participantId = Column(SmallInteger)
    type_event = Column(CHAR(30))
    timestamp = Column(BigInteger)

    def __repr__(self):
        return rep_model(self)