from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer

from destiny.main.bdd import Base
from destiny.utils import rep_model


class ItemEvent(Base):
    __tablename__ = 'itemEvent'

    gameId = Column(BigInteger, nullable=False, primary_key=True)
    itemId = Column(Integer, primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    participantId = Column(Integer)

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = ItemEvent()
    print(a)