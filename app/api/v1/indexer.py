from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.indexer_state import get_indexer_state
from app.db.session import get_db
from app.schemas.indexer import (
    IndexBlockResponse,
    IndexerStatusResponse,
    SyncRequest,
    SyncResultResponse,
    SyncTaskResponse,
)
from app.services.blockchain import blockchain_client
from app.services.indexer import (
    BlockNotAvailableError,
    ChainIDMismatchError,
    blockchain_indexer,
)
from celery.result import AsyncResult

from app.workers.celery_app import celery_app
from app.workers.tasks import sync_confirmed_blocks


router = APIRouter()


@router.post(
    "/block/{block_number}",
    response_model=IndexBlockResponse,
    status_code=status.HTTP_200_OK,
    summary="Index one confirmed blockchain block",
)
async def index_block(
    block_number: int,
    session: AsyncSession = Depends(get_db),
) -> IndexBlockResponse:
    try:
        result = await blockchain_indexer.index_block(
            session=session,
            block_number=block_number,
        )
        return IndexBlockResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except BlockNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ChainIDMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to index block: {exc}",
        ) from exc


@router.get(
    "/status",
    response_model=IndexerStatusResponse,
    summary="Get blockchain indexer status",
)
async def get_status(
    session: AsyncSession = Depends(get_db),
) -> IndexerStatusResponse:
    chain_id = await blockchain_client.get_chain_id()
    blockchain_head = (
        await blockchain_client.get_latest_block_number()
    )
    latest_confirmed_block = max(
        blockchain_head - settings.confirmation_blocks,
        0,
    )

    indexer_state = await get_indexer_state(
        session,
        chain_id,
    )

    return IndexerStatusResponse(
        chain_id=chain_id,
        blockchain_head=blockchain_head,
        latest_confirmed_block=latest_confirmed_block,
        latest_indexed_block=(
            indexer_state.latest_indexed_block
            if indexer_state is not None
            else None
        ),
        confirmation_blocks=settings.confirmation_blocks,
        status=(
            indexer_state.status
            if indexer_state is not None
            else "not_started"
        ),
    )

@router.post(
    "/sync",
    response_model=SyncTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue confirmed-block synchronization",
)
async def start_sync(
    request: SyncRequest,
) -> SyncTaskResponse:
    task = sync_confirmed_blocks.delay(
        batch_size=request.batch_size,
    )

    return SyncTaskResponse(
        status="queued",
        task_id=task.id,
        message="Blockchain synchronization task was queued.",
    )


@router.get(
    "/tasks/{task_id}",
    response_model=SyncResultResponse,
    summary="Get synchronization task status",
)
async def get_sync_task(
    task_id: str,
) -> SyncResultResponse:
    task_result = AsyncResult(
        task_id,
        app=celery_app,
    )

    result: object | None = None

    if task_result.ready():
        try:
            result = task_result.result
        except Exception as exc:
            result = str(exc)

    return SyncResultResponse(
        task_id=task_id,
        state=task_result.state,
        ready=task_result.ready(),
        successful=(
            task_result.successful()
            if task_result.ready()
            else None
        ),
        result=result,
    )