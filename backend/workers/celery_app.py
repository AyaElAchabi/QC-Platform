"""
Celery application configuration
"""
from celery import Celery

from core.config import settings

celery_app = Celery(
    "mlops_qc_worker",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
    include=["workers.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4 hours max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10
)

# Task routing
celery_app.conf.task_routes = {
    "workers.tasks.train_yolo_model": {"queue": "training"}
}