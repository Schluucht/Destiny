from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, BigInteger, Integer, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class TeamStats(Base):
    __tablename__ = 'teamstats'

    gameId = Column(BigInteger, ForeignKey("matches.gameId"), primary_key=True)
    teamId = Column(SmallInteger, primary_key=True)
    firstDragon =  Column(Boolean)
    firstInhibitor = Column(Boolean)
    baronKills = Column(SmallInteger)
    firstRiftHerald = Column(Boolean)
    firstBaron =  Column(Boolean)
    riftHeraldKills = Column(SmallInteger)
    firstBlood = Column(Boolean)
    firstTower = Column(Boolean)
    inhibitorKills = Column(SmallInteger)
    towerKills = Column(SmallInteger)
    win = Column(CHAR(6))
    dragonKills = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
