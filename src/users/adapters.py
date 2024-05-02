from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from src.users.settings import Settings

class DatabaseSchema(DeclarativeBase):
    pass

class DataAccessObject:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.sessionmaker = sessionmaker
        self.session = self.sessionmaker()

    async def begin(self):
        await self.session.begin_nested()

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.close()


class UnitOfWork:
    def __init__(self, engine: AsyncEngine, session: async_sessionmaker[AsyncSession]):
        self.engine = engine
        self.session = session
        
    async def begin(self):
        self.transaction = self.session()
        await self.transaction.begin()

    async def rollback(self):
        await self.transaction.rollback()

    async def close(self):
        await self.transaction.close()

    async def commit(self):
        await self.transaction.commit()

    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.transaction.rollback()
        else:
            await self.transaction.commit()
        await self.close()


class ObjectRelationalMapper:
    def __init__(self, settings: Settings):
        self.settings = settings.orm
        self.engine = create_async_engine(
            settings.orm.uri, 
            echo=settings.orm.engine_echo
        )

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autoflush=self.settings.session_autoflush, 
            autocommit=self.settings.session_autocommit, 
            expire_on_commit=self.settings.session_expire_on_commit
        )