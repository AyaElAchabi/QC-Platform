"""
Feedback model (Active Learning)
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class FeedbackAction(str, enum.Enum):
    CONFIRM = "confirm"
    REFUTE = "refute"
    IGNORE = "ignore"
    CORRECT = "correct"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inference_run_id = Column(UUID(as_uuid=True), ForeignKey("inference_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    detection_index = Column(Integer, nullable=False)
    action = Column(SQLEnum(FeedbackAction), nullable=False, index=True)
    comment = Column(Text)
    corrected_class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"))
    corrected_bbox = Column(JSONB)
    is_hard_example = Column(Boolean, default=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inference_run = relationship("InferenceRun", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback {self.action} (hard={self.is_hard_example})>"