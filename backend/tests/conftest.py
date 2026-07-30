import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.database.session import get_db
from app.main import app

settings = get_settings()


@pytest_asyncio.fixture
async def db_session():
    """Wrap each test in an outer transaction rolled back at teardown.

    Application code calling session.commit() only commits a SAVEPOINT
    (join_transaction_mode="create_savepoint"), so no test data survives
    the test against the real Postgres instance.
    """
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:

            async def override_get_db():
                yield session

            app.dependency_overrides[get_db] = override_get_db
            try:
                yield session
            finally:
                app.dependency_overrides.pop(get_db, None)

        await connection.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
