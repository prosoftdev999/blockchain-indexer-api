import asyncio
from typing import Any

from celery.utils.log import get_task_logger

from app.db.session import AsyncSessionLocal
from app.services.sync import blockchain_sync_service
from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


async def _sync_confirmed_blocks_async(
    batch_size: int | None = None,
) -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        try:
            result = (
                await blockchain_sync_service.sync_confirmed_blocks(
                    session=session,
                    batch_size=batch_size,
                )
            )

            logger.info("Blockchain sync completed: %s", result)

            return result

        except Exception:
            await session.rollback()
            logger.exception("Blockchain synchronization failed.")
            raise


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