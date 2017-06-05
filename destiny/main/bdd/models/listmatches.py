from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model

class ListMatches(Base):
    __tablename__ = 'listMatches'

    summonerId = Column(BigInteger,ForeignKey("players.summonerId"), primary_key=True)
    gameId = Column(BigInteger, ForeignKey("matches.gameId"), primary_key=True)

    def __repr__(self):
        return rep_model(self)