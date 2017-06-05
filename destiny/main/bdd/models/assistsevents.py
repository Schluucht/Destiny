from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class AssistsEvents(Base):
    __tablename__ = 'assistsEvents'
    eventId = Column(BigInteger, primary_key=True)
    participantId = Column(SmallInteger, primary_key=True)

    def __repr__(self):
        return rep_model(self)
