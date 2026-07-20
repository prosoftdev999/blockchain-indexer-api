from fastapi import APIRouter

from app.api.v1.indexer import router as indexer_router


api_router = APIRouter()

api_router.include_router(
    indexer_router,
    prefix="/indexer",
    tags=["Indexer"],
)