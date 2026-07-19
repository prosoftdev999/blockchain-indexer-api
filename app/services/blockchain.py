from typing import Any

from web3 import AsyncHTTPProvider, AsyncWeb3

from app.core.config import settings


class BlockchainClient:
    def __init__(self) -> None:
        self.web3 = AsyncWeb3(
            AsyncHTTPProvider(settings.blockchain_rpc_url)
        )

    async def is_connected(self) -> bool:
        return await self.web3.is_connected()

    async def get_chain_id(self) -> int:
        return await self.web3.eth.chain_id

    async def get_latest_block_number(self) -> int:
        return await self.web3.eth.block_number

    async def get_block(
        self,
        block_identifier: int | str,
        full_transactions: bool = False,
    ) -> Any:
        return await self.web3.eth.get_block(
            block_identifier,
            full_transactions=full_transactions,
        )


blockchain_client = BlockchainClient()