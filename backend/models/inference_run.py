"""
Inference Run model
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class InferenceRun(Base):
    __tablename__ = "inference_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="SET NULL"), index=True)
    external_image_path = Column(String(512))
    predictions = Column(JSONB, nullable=False)
    inference_time_ms = Column(Integer, nullable=False)
    preprocessing_time_ms = Column(Integer)
    postprocessing_time_ms = Column(Integer)
    threshold = Column(Float, default=0.5)
    nms_iou_threshold = Column(Float, default=0.45)
    batch_size = Column(Integer, default=1)
    device = Column(String(20))
    status = Column(String(50), default="completed")
    error_message = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    model = relationship("Model", back_populates="inference_runs")
    image = relationship("Image", back_populates="inference_runs")
    xai_artifacts = relationship("XAIArtifact", back_populates="inference_run", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="inference_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InferenceRun {self.id} ({self.inference_time_ms}ms)>"