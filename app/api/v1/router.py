from fastapi import APIRouter

from app.api.v1.blocks import router as blocks_router
from app.api.v1.indexer import router as indexer_router
from app.api.v1.transactions import router as transactions_router


api_router = APIRouter()

api_router.include_router(
    indexer_router,
    prefix="/indexer",
    tags=["Indexer"],
)

api_router.include_router(
    blocks_router,
    prefix="/blocks",
    tags=["Blocks"],
)

api_router.include_router(
    transactions_router,
    prefix="/transactions",
    tags=["Transactions"],
)