import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.users.settings import Settings
from src.users.adapters import ObjectRelationalMapper as ORM
from src.users.adapters import DataAccessObject as DAO
from src.users.adapters import UnitOfWork as UOW
from src.users.services import Application

@pytest.fixture(scope='function')
async def orm(settings: Settings) -> ORM:
    '''
    Since pytest create a new event loop for each test function, we should pass an instance of the
    engine to every test function. This is because the AsyncEngine do not work in multithread 
    environments. Otherwise, NullPool will be used as the pool class.
    '''
    return ORM(settings)

@pytest.fixture(scope='function')
async def sessionmaker(orm: ORM) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    connection = await orm.engine.connect()
    transaction = await connection.begin()
    sessionmaker = orm.sessionmaker
    sessionmaker.configure(bind=connection)
    yield sessionmaker
    await transaction.rollback()
    await connection.close()

@pytest.fixture(scope='function')
async def dao(sessionmaker: async_sessionmaker[AsyncSession]) -> DAO:
    return DAO(sessionmaker)

@pytest.fixture(scope='function')
async def uow(orm: ORM, sessionmaker) -> UOW:
    return UOW(orm.engine, sessionmaker)

@pytest.fixture(scope='function')
async def application(settings: Settings) -> Application:
    return Application(settings)
