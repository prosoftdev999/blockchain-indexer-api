from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionResponse(BaseModel):
    id: int
    transaction_hash: str
    block_number: int
    transaction_index: int
    from_address: str
    to_address: str | None
    value: Decimal
    gas: int
    gas_price: Decimal | None
    nonce: int
    input_data: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    limit: int
    offset: int