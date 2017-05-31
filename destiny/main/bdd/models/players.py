from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, DATE

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Players(Base):
    __tablename__ = 'players'

    summonerId = Column(BigInteger, primary_key=True)
    accountId = Column(BigInteger)
    tier = Column(CHAR(12))
    lastRefresh = Column(DATE)

    def __repr__(self):
        return rep_model(self)