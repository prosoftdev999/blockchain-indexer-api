from celery import Celery
from celery.schedules import schedule

from app.core.config import settings


celery_app = Celery(
    "blockchain_indexer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
)

celery_app.conf.beat_schedule = {
    "sync-confirmed-blocks": {
        "task": "app.workers.tasks.sync_confirmed_blocks",
        "schedule": schedule(
            run_every=settings.sync_interval_seconds,
        ),
    },
}