from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, Integer

from models import Base, rep_model


class ItemEvent(Base):
    __tablename__ = 'itemEvent'

    gameId = Column(BigInteger, nullable=False, primary_key=True)
    itemId = Column(Integer, primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    participant = Column(CHAR(50))

    def __repr__(self):
        return rep_model(self)

if __name__ == '__main__':
    a = ItemEvent()
    print(a)