from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


async def get_transaction_by_hash(
    session: AsyncSession,
    transaction_hash: str,
) -> Transaction | None:
    normalized_hash = transaction_hash.lower()

    result = await session.execute(
        select(Transaction).where(
            func.lower(Transaction.transaction_hash) == normalized_hash
        )
    )

    return result.scalar_one_or_none()


async def list_transactions(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> tuple[list[Transaction], int]:
    total_result = await session.execute(
        select(func.count(Transaction.id))
    )
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(Transaction)
        .order_by(
            Transaction.block_number.desc(),
            Transaction.transaction_index.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    transactions = list(result.scalars().all())

    return transactions, total


async def list_transactions_by_address(
    session: AsyncSession,
    address: str,
    limit: int,
    offset: int,
) -> tuple[list[Transaction], int]:
    normalized_address = address.lower()

    address_filter = or_(
        func.lower(Transaction.from_address) == normalized_address,
        func.lower(Transaction.to_address) == normalized_address,
    )

    total_result = await session.execute(
        select(func.count(Transaction.id)).where(address_filter)
    )
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(Transaction)
        .where(address_filter)
        .order_by(
            Transaction.block_number.desc(),
            Transaction.transaction_index.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    transactions = list(result.scalars().all())

    return transactions, total