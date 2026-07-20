from sqlalchemy import func, select
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


async def list_blocks(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> tuple[list[Block], int]:
    total_result = await session.execute(
        select(func.count(Block.id))
    )
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(Block)
        .order_by(Block.number.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(result.scalars().all()), total