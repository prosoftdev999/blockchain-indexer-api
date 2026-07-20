from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blockchain Indexer API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/blockchain_indexer"
    )

    redis_url: str = "redis://localhost:6379/0"

    blockchain_rpc_url: str = "https://ethereum-sepolia-rpc.publicnode.com"
    blockchain_chain_id: int = 11155111
    start_block: int = 0
    confirmation_blocks: int = 12
    indexer_batch_size: int = 10

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    sync_batch_size: int = 5
    sync_interval_seconds: int = 30
    sync_lock_name: str = "blockchain-indexer:sync-lock"
    sync_lock_timeout_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()