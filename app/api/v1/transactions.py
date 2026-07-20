from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.transaction import (
    get_transaction_by_hash,
    list_transactions,
    list_transactions_by_address,
)
from app.db.session import get_db
from app.schemas.transaction import (
    TransactionListResponse,
    TransactionResponse,
)


router = APIRouter()


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List indexed transactions",
)
async def get_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    transactions, total = await list_transactions(
        session=session,
        limit=limit,
        offset=offset,
    )

    return TransactionListResponse(
        items=[
            TransactionResponse.model_validate(transaction)
            for transaction in transactions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{transaction_hash}",
    response_model=TransactionResponse,
    summary="Get one indexed transaction",
)
async def get_transaction(
    transaction_hash: str,
    session: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    transaction = await get_transaction_by_hash(
        session=session,
        transaction_hash=transaction_hash,
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction was not found.",
        )

    return TransactionResponse.model_validate(transaction)


@router.get(
    "/address/{address}/history",
    response_model=TransactionListResponse,
    summary="List indexed transactions for an address",
)
async def get_address_transactions(
    address: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    transactions, total = await list_transactions_by_address(
        session=session,
        address=address,
        limit=limit,
        offset=offset,
    )

    return TransactionListResponse(
        items=[
            TransactionResponse.model_validate(transaction)
            for transaction in transactions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )