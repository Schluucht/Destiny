from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, BigInteger, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Timelines(Base):
    __tablename__ = 'timelines'

    gameId = Column(BigInteger, ForeignKey("participants.gameId"), primary_key=True)
    participantId = Column(SmallInteger, primary_key=True) # ForeignKey("participants.participantId"),
    timestamp =  Column(BigInteger, primary_key=True)

    def __repr__(self):
        return rep_model(self)
