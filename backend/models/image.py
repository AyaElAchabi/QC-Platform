"""
Modèle Image pour la base de données
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
