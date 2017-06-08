from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, BigInteger, Integer, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Bans(Base):
    __tablename__ = 'bans'

    gameId = Column(BigInteger, ForeignKey("teamstats.gameId"), primary_key=True)
    teamId = Column(SmallInteger, primary_key=True)
    pickTurn = Column(SmallInteger)
    championId = Column(SmallInteger, primary_key=True)

    def __repr__(self):
        return rep_model(self)
