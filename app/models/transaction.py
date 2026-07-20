from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.block import Block


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_hash: Mapped[str] = mapped_column(
        String(66),
        unique=True,
        nullable=False,
        index=True,
    )

    block_number: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "blocks.number",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    transaction_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    from_address: Mapped[str] = mapped_column(
        String(42),
        nullable=False,
        index=True,
    )

    to_address: Mapped[str | None] = mapped_column(
        String(42),
        nullable=True,
        index=True,
    )

    value: Mapped[Decimal] = mapped_column(
        Numeric(78, 0),
        nullable=False,
        default=0,
    )

    gas: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    gas_price: Mapped[Decimal | None] = mapped_column(
        Numeric(78, 0),
        nullable=True,
    )

    nonce: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    input_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="0x",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    block: Mapped["Block"] = relationship(
        back_populates="transactions",
    )