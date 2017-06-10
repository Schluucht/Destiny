from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Participants(Base):
    __tablename__ = 'participants'

    gameId = Column(BigInteger, ForeignKey("matches.gameId"), primary_key=True)
    participantId = Column(SmallInteger, primary_key=True)
    teamId = Column(SmallInteger)
    highestAchievedSeasonTier = Column(CHAR(12))
    championId = Column(SmallInteger)
    spell1Id = Column(SmallInteger)
    spell2Id = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
