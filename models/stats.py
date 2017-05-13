from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer

from models import Base, rep_model


class Stats(Base):
    __tablename__ = 'stats'

    idStats = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    gameId = Column(BigInteger, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    championId = Column(CHAR(50))
    level = Column(Integer)
    currentGold = Column(Integer)
    minionsKilled = Column(Integer)
    xp = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = Stats()
    print(a)