from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
import uuid
from datetime import datetime


class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    
    # Configuration
    model_name = Column(String, nullable=False)
    epochs = Column(Integer, nullable=False)
    batch_size = Column(Integer, nullable=False)
    img_size = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    patience = Column(Integer, nullable=False)
    config = Column(JSON)
    
    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)
    current_epoch = Column(Integer, default=0)
    
    # Metrics
    metrics = Column(JSON)  # loss, map50, precision, recall
    
    # Paths
    dataset_path = Column(String)
    model_path = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Error
    error_message = Column(String)
