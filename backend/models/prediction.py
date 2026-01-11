"""
Prediction model (inference results)
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    image_path = Column(String(512))
    results = Column(JSONB, nullable=False)  # Liste des détections
    inference_time_ms = Column(Float, nullable=False)
    confidence_threshold = Column(Float, default=0.25)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    model = relationship("Model")
    user = relationship("User")

    def __repr__(self):
        return f"<Prediction {self.id} - Model: {self.model_id} - {len(self.results.get('detections', []))} détections>"
