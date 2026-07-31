from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings


@asynccontextmanager
async def get_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    """Yields an AsyncPostgresSaver pointed at the app's own Postgres
    instance. Assumes `setup()` has already been run once against this
    database (see scripts/setup_langgraph_checkpointer.py) — this module
    only opens connections, it never creates/migrates the checkpoint tables
    itself, per the milestone's "use the library's own setup utility, don't
    hand-design these" instruction.
    """
    dsn = get_settings().psycopg_database_url
    async with AsyncPostgresSaver.from_conn_string(dsn) as saver:
        yield saver
