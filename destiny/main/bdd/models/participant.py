from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, CHAR

from destiny.main.bdd import Base
from destiny.utils import rep_model


class Participant(Base):
    __tablename__ = 'participant'

    gameId = Column(BigInteger, primary_key=True, nullable=False)
    participantId = Column(Integer, primary_key=True)
    role = Column(CHAR(20))
    championId = Column(Integer)

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = Participant()
    print(a)