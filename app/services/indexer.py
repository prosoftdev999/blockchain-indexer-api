from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.block import get_block_by_number
from app.crud.indexer_state import update_indexer_state
from app.models.block import Block
from app.models.transaction import Transaction
from app.services.blockchain import blockchain_client


class BlockNotAvailableError(Exception):
    """Raised when a requested block is newer than the confirmed chain head."""


class ChainIDMismatchError(Exception):
    """Raised when the RPC network does not match the configured chain."""


def to_hex_string(value: object | None) -> str:
    """
    Convert Web3 HexBytes, bytes, strings, or other values to a 0x-prefixed
    hexadecimal string.
    """

    if value is None:
        return "0x"

    if isinstance(value, str):
        if value.startswith("0x"):
            return value

        return f"0x{value}"

    if isinstance(value, bytes):
        return f"0x{value.hex()}"

    hex_method = getattr(value, "hex", None)

    if callable(hex_method):
        hex_value = hex_method()

        if isinstance(hex_value, str):
            if hex_value.startswith("0x"):
                return hex_value

            return f"0x{hex_value}"

    return str(value)


class BlockchainIndexer:
    async def verify_chain(self) -> int:
        """
        Verify that the connected RPC network matches the configured chain ID.
        """

        chain_id = await blockchain_client.get_chain_id()

        if chain_id != settings.blockchain_chain_id:
            raise ChainIDMismatchError(
                f"Expected chain ID {settings.blockchain_chain_id}, "
                f"but RPC returned {chain_id}."
            )

        return chain_id

    async def get_confirmed_block_number(self) -> int:
        """
        Return the most recent block considered safe after confirmation delay.
        """

        latest_block = await blockchain_client.get_latest_block_number()

        return max(
            latest_block - settings.confirmation_blocks,
            0,
        )

    async def _count_block_transactions(
        self,
        session: AsyncSession,
        block_number: int,
    ) -> int:
        """
        Count stored transactions for one indexed block.
        """

        result = await session.execute(
            select(func.count(Transaction.id)).where(
                Transaction.block_number == block_number
            )
        )

        return int(result.scalar_one())

    async def index_block(
        self,
        session: AsyncSession,
        block_number: int,
    ) -> dict[str, Any]:
        """
        Fetch one confirmed blockchain block and persist the block and all of
        its transactions in PostgreSQL.
        """

        if block_number < 0:
            raise ValueError("Block number cannot be negative.")

        chain_id = await self.verify_chain()
        confirmed_block = await self.get_confirmed_block_number()

        if block_number > confirmed_block:
            raise BlockNotAvailableError(
                f"Block {block_number} is not confirmed yet. "
                f"Latest confirmed block is {confirmed_block}."
            )

        existing_block = await get_block_by_number(
            session=session,
            block_number=block_number,
        )

        if existing_block is not None:
            transaction_count = await self._count_block_transactions(
                session=session,
                block_number=block_number,
            )

            return {
                "status": "success",
                "block_number": existing_block.number,
                "block_hash": existing_block.block_hash,
                "transactions_indexed": transaction_count,
                "already_indexed": True,
            }

        blockchain_block = await blockchain_client.get_block(
            block_identifier=block_number,
            full_transactions=True,
        )

        block_hash = to_hex_string(blockchain_block["hash"])
        parent_hash = to_hex_string(blockchain_block["parentHash"])

        block_timestamp = datetime.fromtimestamp(
            blockchain_block["timestamp"],
            tz=timezone.utc,
        )

        transactions = blockchain_block["transactions"]

        database_block = Block(
            number=int(blockchain_block["number"]),
            block_hash=block_hash,
            parent_hash=parent_hash,
            timestamp=block_timestamp,
            transaction_count=len(transactions),
        )

        session.add(database_block)

        for transaction in transactions:
            gas_price = transaction.get("gasPrice")
            to_address = transaction.get("to")
            input_value = transaction.get("input")

            database_transaction = Transaction(
                transaction_hash=to_hex_string(transaction["hash"]),
                block_number=int(blockchain_block["number"]),
                transaction_index=int(transaction["transactionIndex"]),
                from_address=str(transaction["from"]),
                to_address=(
                    str(to_address)
                    if to_address is not None
                    else None
                ),
                value=Decimal(int(transaction["value"])),
                gas=int(transaction["gas"]),
                gas_price=(
                    Decimal(int(gas_price))
                    if gas_price is not None
                    else None
                ),
                nonce=int(transaction["nonce"]),
                input_data=to_hex_string(input_value),
            )

            session.add(database_transaction)

        await update_indexer_state(
            session=session,
            chain_id=chain_id,
            latest_indexed_block=block_number,
            latest_confirmed_block=confirmed_block,
            status="idle",
            last_error=None,
        )

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return {
            "status": "success",
            "block_number": block_number,
            "block_hash": block_hash,
            "transactions_indexed": len(transactions),
            "already_indexed": False,
        }


blockchain_indexer = BlockchainIndexer()