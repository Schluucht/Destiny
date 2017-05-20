from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer

from destiny.main.bdd.base import Base, rep_model


class Matches(Base):
    __tablename__ = 'matches'

    gameId = Column(BigInteger, primary_key=True, nullable=False)
    platformId = Column(CHAR(9))
    season = Column(Integer)
    # fixme why do not use timestamp type?
    timestamp = Column(BigInteger)

    def __repr__(self):
        return rep_model(self)


if __name__ == '__main__':
    a = Matches()
    print(a)