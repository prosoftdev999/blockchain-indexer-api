from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.indexer_state import get_indexer_state
from app.db.session import get_db
from app.schemas.indexer import (
    IndexBlockResponse,
    IndexerStatusResponse,
)
from app.services.blockchain import blockchain_client
from app.services.indexer import (
    BlockNotAvailableError,
    ChainIDMismatchError,
    blockchain_indexer,
)


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