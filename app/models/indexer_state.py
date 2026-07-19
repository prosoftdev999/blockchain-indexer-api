from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class IndexerState(Base):
    __tablename__ = "indexer_states"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    chain_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    latest_indexed_block: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    latest_confirmed_block: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="idle",
    )
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )