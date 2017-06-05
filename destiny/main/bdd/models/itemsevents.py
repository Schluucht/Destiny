from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class ItemsEvents(Base):
    __tablename__ = 'itemsEvents'
    eventId = Column(BigInteger, primary_key=True)
    itemId = Column(SmallInteger)
    eventType = Column(CHAR(20))

    def __repr__(self):
        return rep_model(self)
