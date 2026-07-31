"""One-time (idempotent) setup for langgraph-checkpoint-postgres's own
checkpoint/checkpoint_blobs/checkpoint_writes tables, run against the same
database as the app's own Alembic-managed schema.

Deliberately NOT an Alembic migration — the library owns and versions the
shape of its own tables via `AsyncPostgresSaver.setup()`; hand-writing a
migration for them would fight the library on every future upgrade.

Usage:
    python -m scripts.setup_langgraph_checkpointer
"""

import asyncio

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings


async def main() -> None:
    dsn = get_settings().psycopg_database_url
    async with AsyncPostgresSaver.from_conn_string(dsn) as saver:
        await saver.setup()


if __name__ == "__main__":
    asyncio.run(main())
