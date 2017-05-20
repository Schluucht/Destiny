from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer

from destiny.main.bdd.base import Base, rep_model


class Participant(Base):
    __tablename__ = 'participant'

    gameId = Column(BigInteger, primary_key=True, nullable=False)
    participantId = Column(Integer, primary_key=True)
    championId = Column(Integer)

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = Participant()
    print(a)