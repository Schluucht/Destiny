from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class BuildingEvents(Base):
    __tablename__ = 'buildingEvents'
    eventId = Column(BigInteger, primary_key=True)
    buildingType = Column(CHAR(20))
    towerType = Column(CHAR(20))
    teamId = Column(SmallInteger)
    laneType = Column(CHAR(20))
    x = Column(SmallInteger)
    y = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
