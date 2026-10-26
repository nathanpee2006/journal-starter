import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import get_settings
from api.logging_config import configure_logging
from api.repositories.postgres_repository import PostgresDB
from api.routers.journal_router import router as journal_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    configure_logging()
    settings = get_settings()
    async with PostgresDB(settings.database_url) as database:
        app.state.database = database
        try:
            # TODO (Task 3): Log API readiness at INFO after the database is ready.
            # Setup phasee
            logger.info("database: ready")
            logger.info("application: serving")
            yield  # Application is now serving requests by transfering control
        finally:
            # TODO (Task 3): Log API shutdown at INFO during cleanup.
            # Cleanup phase
            logger.info("application: shutting down")
            logger.info("database: closed")
            del app.state.database


app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
    lifespan=lifespan,
)
app.include_router(journal_router)
