from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.block import get_block_by_number, list_blocks
from app.db.session import get_db
from app.schemas.block import BlockListResponse, BlockResponse


router = APIRouter()


@router.get(
    "",
    response_model=BlockListResponse,
    summary="List indexed blocks",
)
async def get_blocks(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> BlockListResponse:
    blocks, total = await list_blocks(
        session=session,
        limit=limit,
        offset=offset,
    )

    return BlockListResponse(
        items=[BlockResponse.model_validate(block) for block in blocks],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{block_number}",
    response_model=BlockResponse,
    summary="Get one indexed block",
)
async def get_block(
    block_number: int,
    session: AsyncSession = Depends(get_db),
) -> BlockResponse:
    block = await get_block_by_number(
        session=session,
        block_number=block_number,
    )

    if block is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block {block_number} was not found.",
        )

    return BlockResponse.model_validate(block)