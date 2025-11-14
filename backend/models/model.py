"""
Model model (trained ML model)
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.database import Base


class ModelStage(str, enum.Enum):
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_job_id = Column(UUID(as_uuid=True), ForeignKey("training_jobs.id", ondelete="SET NULL"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    task_type = Column(String(50), nullable=False)
    architecture = Column(String(100), nullable=False)
    storage_path = Column(String(512), nullable=False)
    mlflow_model_uri = Column(String(512))
    metrics = Column(JSONB, nullable=False)
    hyperparameters = Column(JSONB)
    stage = Column(SQLEnum(ModelStage), default=ModelStage.STAGING, index=True)
    is_active = Column(Boolean, default=True, index=True)
    inference_count = Column(Integer, default=0)
    avg_inference_time_ms = Column(Float)
    model_card_path = Column(String(512))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    promoted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    promoted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    training_job = relationship("TrainingJob", back_populates="models")
    project = relationship("Project", back_populates="models")
    inference_runs = relationship("InferenceRun", back_populates="model")

    def __repr__(self):
        return f"<Model {self.name} v{self.version} ({self.stage})>"