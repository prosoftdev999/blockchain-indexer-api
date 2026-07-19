from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import AsyncSessionLocal

from app.services.blockchain import blockchain_client

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-style API for indexing EVM blockchain blocks, "
        "transactions, receipts, and smart-contract events."
    ),
)


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, object]:
    database_status = "unhealthy"
    redis_status = "unhealthy"
    blockchain_status = "unhealthy"

    chain_id: int | None = None
    latest_block: int | None = None

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"

    redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        await redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    finally:
        await redis_client.aclose()

    try:
        connected = await blockchain_client.is_connected()

        if connected:
            chain_id = await blockchain_client.get_chain_id()
            latest_block = (
                await blockchain_client.get_latest_block_number()
            )
            blockchain_status = "healthy"
    except Exception:
        blockchain_status = "unhealthy"

    overall_status = (
        "healthy"
        if (
            database_status == "healthy"
            and redis_status == "healthy"
            and blockchain_status == "healthy"
        )
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "service": settings.app_name,
        "database": database_status,
        "redis": redis_status,
        "blockchain": blockchain_status,
        "chain_id": chain_id,
        "latest_block": latest_block,
        "debug": settings.debug,
    }