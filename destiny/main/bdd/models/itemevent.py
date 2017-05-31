from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class ItemEvent(Base):
    __tablename__ = 'itemEvent'
    eventId = Column(BigInteger, primary_key=True)
    itemId = Column(SmallInteger)
    eventType = Column(CHAR(20))

    def __repr__(self):
        return rep_model(self)
