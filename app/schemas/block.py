from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlockResponse(BaseModel):
    id: int
    number: int
    block_hash: str
    parent_hash: str
    timestamp: datetime
    transaction_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlockListResponse(BaseModel):
    items: list[BlockResponse]
    total: int
    limit: int
    offset: int