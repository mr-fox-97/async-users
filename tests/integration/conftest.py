import pytest
import socket
import asyncio

from typing import AsyncGenerator
from typing import Any

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

@pytest.fixture(scope='session')
async def engine(url : URL) -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(url)
    yield engine
    await engine.dispose()

@pytest.fixture(scope='module')
async def session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    yield async_sessionmaker(
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession
    )

@pytest.fixture(scope='function')
async def session(engine : AsyncEngine, session_factory : async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = session_factory(bind=connection)
    await session.begin()
    yield session
    await session.close()
    await transaction.rollback()
    await connection.close()