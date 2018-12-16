
from sqlalchemy import Column, Integer, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship, backref

from ..support import Base
from ..types import Str


class ActivitySimilarity(Base):

    __tablename__ = 'activity_similarity'

    id = Column(Integer, primary_key=True)
    constraint = Column(Str, index=True)
    activity_journal_lo_id = Column(Integer, ForeignKey('activity_journal.id', ondelete='cascade'), index=True)
    activity_journal_hi_id = Column(Integer, ForeignKey('activity_journal.id', ondelete='cascade'), index=True)
    similarity = Column(Float, nullable=False)
    UniqueConstraint(constraint, activity_journal_lo_id)
    UniqueConstraint(constraint, activity_journal_hi_id)


class ActivityNearby(Base):

    __tablename__ = 'activity_nearby'

    id = Column(Integer, primary_key=True)
    constraint = Column(Str, index=True)
    group = Column(Integer, nullable=False, index=True)
    activity_journal_id = Column(Integer, ForeignKey('activity_journal.id', ondelete='cascade'))
    activity_journal = relationship('ActivityJournal',
                                    backref=backref('nearby', cascade='all, delete-orphan',
                                                    passive_deletes=True))
    UniqueConstraint(constraint, activity_journal_id)