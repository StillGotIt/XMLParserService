from src.infra.db.sql.db import AsyncPostgresClient
from src.infra.db.sql.models.base import Base


async def run_migrations():
    client: AsyncPostgresClient = AsyncPostgresClient()
    async with client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
