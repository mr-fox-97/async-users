import pytest
import socket
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.settings import URL, Settings
from src.settings import SQLAlchemySettings, FastAPISettings
from src.services import ObjectRelationalMapper as ORM
from src.adapters import DataAccessObject as DAO
from src.adapters import UnitOfWork as UOW
from src.services import Application

@pytest.fixture(scope='session')
def url() -> URL:
    return URL.create(
        drivername = 'postgresql+asyncpg',
        username = 'postgres',
        password = 'postgres',
        host = socket.gethostbyname('postgres'),
        port = 5432,
        database = 'postgres'
    )

@pytest.fixture(scope='session')
def settings(url: URL) -> Settings:
    return Settings(
        orm=SQLAlchemySettings(
            uri=url,
            engine_echo=True,
            session_autoflush=False,
            session_autocommit=False,
            session_expire_on_commit=False
        )
    )

@pytest.fixture(scope='function')
async def orm(settings: Settings) -> ORM:
    return ORM(settings)

@pytest.fixture(scope='function')
async def uow(orm: ORM) -> AsyncGenerator[UOW, None]:
    uow = UOW(orm)
    connection = await uow.engine.connect()
    transaction = await connection.begin()
    uow.session = orm.sessionmaker(bind=connection)
    yield uow
    await transaction.rollback()
    await connection.close()
