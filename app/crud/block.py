from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.block import Block


async def get_block_by_number(
    session: AsyncSession,
    block_number: int,
) -> Block | None:
    result = await session.execute(
        select(Block).where(Block.number == block_number)
    )
    return result.scalar_one_or_none()


async def get_block_by_hash(
    session: AsyncSession,
    block_hash: str,
) -> Block | None:
    result = await session.execute(
        select(Block).where(Block.block_hash == block_hash)
    )
    return result.scalar_one_or_none()