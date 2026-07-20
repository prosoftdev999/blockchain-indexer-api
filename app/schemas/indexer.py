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