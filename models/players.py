from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, DATE

from models.base import Base, rep_model


class Players(Base):
    __tablename__ = 'players'

    summonerId = Column(BigInteger, primary_key=True, nullable=False)
    accountId = Column(BigInteger, nullable=False)
    tier = Column(CHAR(12))
    last_refresh = Column(DATE, nullable=False)

    def __repr__(self):
        return rep_model(self)


if __name__ == '__main__':
    a = Players(summonerId=1, accountId=1, tier="GOLD")
    print(a)