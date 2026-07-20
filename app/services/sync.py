from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.indexer_state import get_indexer_state
from app.services.blockchain import blockchain_client
from app.services.indexer import blockchain_indexer


class BlockchainSyncService:
    async def sync_confirmed_blocks(
        self,
        session: AsyncSession,
        batch_size: int | None = None,
    ) -> dict[str, Any]:
        chain_id = await blockchain_indexer.verify_chain()

        blockchain_head = (
            await blockchain_client.get_latest_block_number()
        )

        latest_confirmed_block = max(
            blockchain_head - settings.confirmation_blocks,
            0,
        )

        state = await get_indexer_state(
            session=session,
            chain_id=chain_id,
        )

        if state is None:
            start_block = settings.start_block
        else:
            start_block = state.latest_indexed_block + 1

        effective_batch_size = (
            batch_size
            if batch_size is not None
            else settings.sync_batch_size
        )

        if effective_batch_size < 1:
            raise ValueError("Batch size must be at least 1.")

        if start_block > latest_confirmed_block:
            return {
                "status": "up_to_date",
                "chain_id": chain_id,
                "blockchain_head": blockchain_head,
                "latest_confirmed_block": latest_confirmed_block,
                "start_block": start_block,
                "end_block": None,
                "blocks_indexed": 0,
            }

        end_block = min(
            start_block + effective_batch_size - 1,
            latest_confirmed_block,
        )

        indexed_blocks: list[int] = []

        for block_number in range(start_block, end_block + 1):
            result = await blockchain_indexer.index_block(
                session=session,
                block_number=block_number,
            )

            indexed_blocks.append(result["block_number"])

        return {
            "status": "success",
            "chain_id": chain_id,
            "blockchain_head": blockchain_head,
            "latest_confirmed_block": latest_confirmed_block,
            "start_block": start_block,
            "end_block": end_block,
            "blocks_indexed": len(indexed_blocks),
            "indexed_block_numbers": indexed_blocks,
        }


blockchain_sync_service = BlockchainSyncService()