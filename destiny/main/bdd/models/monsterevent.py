from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import BigInteger, CHAR, SmallInteger

from destiny.main.bdd import Base
from destiny.utils import rep_model


class MonsterEvent(Base):
    __tablename__ = 'monsterEvent'

    eventId = Column(BigInteger, primary_key=True)
    monsterType = Column(CHAR(20))
    monsterSubType = Column(CHAR(20))
    x = Column(SmallInteger)
    y = Column(SmallInteger)

    def __repr__(self):
        return rep_model(self)
