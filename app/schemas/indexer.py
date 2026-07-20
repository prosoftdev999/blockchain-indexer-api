from typing import Any

from pydantic import BaseModel, Field


class IndexBlockResponse(BaseModel):
    status: str
    block_number: int
    block_hash: str
    transactions_indexed: int = Field(ge=0)
    already_indexed: bool


class IndexerStatusResponse(BaseModel):
    chain_id: int
    blockchain_head: int
    latest_confirmed_block: int
    latest_indexed_block: int | None
    confirmation_blocks: int
    status: str


class SyncRequest(BaseModel):
    batch_size: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of confirmed blocks to index.",
    )


class SyncTaskResponse(BaseModel):
    status: str
    task_id: str
    message: str


class SyncResultResponse(BaseModel):
    task_id: str
    state: str
    ready: bool
    successful: bool | None
    result: Any | None