from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(String, ForeignKey("users.id"))
    task_type = Column(String, default="detection")
    status = Column(String, default="active")
    classes = Column(JSON)
    labelstudio_project_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    labelstudio_project_id = Column(String, nullable=True)
    
    # Relationships
    models = relationship("Model", back_populates="project")
