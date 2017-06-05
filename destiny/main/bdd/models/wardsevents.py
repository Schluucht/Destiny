from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR

from destiny.main.bdd import Base
from destiny.utils import rep_model


class WardsEvents(Base):
    __tablename__ = 'wardsEvents'
    eventId = Column(BigInteger, primary_key=True)
    eventType = Column( CHAR(20))
    wardType = Column(CHAR(20))

    def __repr__(self):
        return rep_model(self)
