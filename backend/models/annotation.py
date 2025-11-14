"""
Annotation model
"""
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from core.database import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True)
    image_id = Column(String, ForeignKey("images.id"))
    class_name = Column(String, nullable=False)
    bbox = Column(JSON, nullable=False)  # {x, y, width, height}
    confidence = Column(Float, default=1.0)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
