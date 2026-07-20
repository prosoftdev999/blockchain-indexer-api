from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indexer_state import IndexerState


async def get_indexer_state(
    session: AsyncSession,
    chain_id: int,
) -> IndexerState | None:
    result = await session.execute(
        select(IndexerState).where(IndexerState.chain_id == chain_id)
    )
    return result.scalar_one_or_none()


async def update_indexer_state(
    session: AsyncSession,
    chain_id: int,
    latest_indexed_block: int,
    latest_confirmed_block: int,
    status: str = "idle",
    last_error: str | None = None,
) -> IndexerState:
    state = await get_indexer_state(session, chain_id)

    if state is None:
        state = IndexerState(
            chain_id=chain_id,
            latest_indexed_block=latest_indexed_block,
            latest_confirmed_block=latest_confirmed_block,
            status=status,
            last_error=last_error,
        )
        session.add(state)
    else:
        state.latest_indexed_block = latest_indexed_block
        state.latest_confirmed_block = latest_confirmed_block
        state.status = status
        state.last_error = last_error

    return state
