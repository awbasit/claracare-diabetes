from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

# A zero-arg callable that returns a fresh AsyncSession usable as an async
# context manager (`async with session_factory() as db: ...`) — satisfied by
# `app.database.session.AsyncSessionLocal` in production. Nodes/tools take
# this instead of a live AsyncSession because InterviewState is checkpointed
# to Postgres: a DB session can't be part of that persisted state, so each
# node/tool opens its own short-lived session per invocation instead.
SessionFactory = Callable[[], AsyncSession]
