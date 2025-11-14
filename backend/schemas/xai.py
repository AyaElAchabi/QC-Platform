"""
XAI (Explainability) schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from models.xai_artifact import XAIMethod


class XAIRequest(BaseModel):
    inference_run_id: UUID
    detection_index: int = Field(..., ge=0)
    methods: List[XAIMethod] = [XAIMethod.GRADCAM, XAIMethod.SHAP]


class XAIArtifactResponse(BaseModel):
    id: UUID
    method: XAIMethod
    storage_path: str
    heatmap_url: Optional[str] = None
    consensus_score: Optional[float]
    generation_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class XAIComparisonResponse(BaseModel):
    artifacts: List[XAIArtifactResponse]
    consensus_score: float
    recommendation: str