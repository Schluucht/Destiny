from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Stats(Base):
    __tablename__ = 'stats'

    gameId = Column(BigInteger, primary_key=True)
    participantId = Column(SmallInteger, primary_key=True )
    timestamp = Column(BigInteger, primary_key=True)
    level = Column(SmallInteger)
    currentGold = Column(Integer)
    minionsKilled = Column(SmallInteger)
    xp = Column(Integer)
    jungleMinionsKilled = Column(SmallInteger)
    x = Column(SmallInteger)
    y = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
