from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Matches(Base):
    __tablename__ = 'matches'

    gameId = Column(BigInteger, primary_key=True)
    platformId = Column(CHAR(9))
    season = Column(Integer)
    gameVersion = Column(CHAR(20))
    # fixme why do not use timestamp type?
    timestamp = Column(BigInteger)

    def __repr__(self):
        return rep_model(self)
