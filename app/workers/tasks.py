import asyncio
from typing import Any

from celery.utils.log import get_task_logger
from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.sync import blockchain_sync_service
from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


async def _sync_confirmed_blocks_async(
    batch_size: int | None = None,
) -> dict[str, Any]:
    redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    lock = redis_client.lock(
        name=settings.sync_lock_name,
        timeout=settings.sync_lock_timeout_seconds,
        blocking=False,
    )

    lock_acquired = False

    try:
        lock_acquired = await lock.acquire()

        if not lock_acquired:
            result = {
                "status": "skipped",
                "reason": "Another blockchain synchronization task is running.",
                "blocks_indexed": 0,
            }

            logger.info("Blockchain sync skipped: lock already held.")

            return result

        async with AsyncSessionLocal() as session:
            try:
                result = (
                    await blockchain_sync_service.sync_confirmed_blocks(
                        session=session,
                        batch_size=batch_size,
                    )
                )

                logger.info(
                    "Blockchain sync completed: %s",
                    result,
                )

                return result

            except Exception:
                await session.rollback()
                logger.exception(
                    "Blockchain synchronization failed."
                )
                raise

    finally:
        if lock_acquired:
            try:
                await lock.release()
            except Exception:
                logger.exception(
                    "Failed to release blockchain sync lock."
                )

        await redis_client.aclose()


@celery_app.task(
    bind=True,
    name="app.workers.tasks.sync_confirmed_blocks",
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=5,
)
def sync_confirmed_blocks(
    self,
    batch_size: int | None = None,
) -> dict[str, Any]:
    return asyncio.run(
        _sync_confirmed_blocks_async(
            batch_size=batch_size,
        )
    )