"""
XAI Artifact model
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class XAIMethod(str, enum.Enum):
    GRADCAM = "gradcam"
    SHAP = "shap"
    INTEGRATED_GRADIENTS = "integrated_gradients"
    LIME = "lime"


class XAIArtifact(Base):
    __tablename__ = "xai_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inference_run_id = Column(UUID(as_uuid=True), ForeignKey("inference_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="SET NULL"), index=True)
    detection_index = Column(Integer, nullable=False)
    method = Column(SQLEnum(XAIMethod), nullable=False, index=True)
    storage_path = Column(String(512), nullable=False)
    heatmap_base64 = Column(Text)
    consensus_score = Column(Float)
    generation_time_ms = Column(Integer, nullable=False)
    parameters = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inference_run = relationship("InferenceRun", back_populates="xai_artifacts")

    def __repr__(self):
        return f"<XAIArtifact {self.method} ({self.generation_time_ms}ms)>"