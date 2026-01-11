"""
XAI (Explainable AI) Service Module
Provides visual and numerical explanations for model predictions
"""
from .xai_service import YOLOv8XAIService, create_xai_service

__all__ = ["YOLOv8XAIService", "create_xai_service"]
