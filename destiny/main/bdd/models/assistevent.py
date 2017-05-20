from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer

from destiny.main.bdd.base import Base, rep_model


class AssistEvent(Base):
    __tablename__ = 'assistEvent'

    gameId = Column(BigInteger, nullable=False, primary_key=True)
    assist = Column(CHAR(50), primary_key=True)
    victim = Column(CHAR(50), primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = AssistEvent()
    print(a)