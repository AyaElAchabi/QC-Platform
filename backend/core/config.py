"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # App
    APP_NAME: str = "MLOps QC Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600
    
    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "mlops-qc"
    
    # RabbitMQ
    RABBITMQ_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str = "visual-qc"
    
    # DVC
    DVC_REMOTE: str
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_FORMATS: List[str] = ["jpeg", "jpg", "png"]
    
    # Model Inference
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
    DEFAULT_NMS_IOU_THRESHOLD: float = 0.45
    MAX_BATCH_SIZE: int = 16


settings = Settings()