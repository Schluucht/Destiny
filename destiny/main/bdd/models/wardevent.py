from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR

from destiny.main.bdd import Base
from destiny.utils import rep_model


class WardEvent(Base):
    __tablename__ = 'wardEvent'
    eventId = Column(BigInteger, primary_key=True)
    eventType = Column( CHAR(20))
    wardType = Column(CHAR(20))

    def __repr__(self):
        return rep_model(self)
