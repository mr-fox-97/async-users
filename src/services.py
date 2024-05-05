from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.settings import Settings
from queue import Queue

class ObjectRelationalMapper:
    def __init__(self, settings: Settings):
        self.settings = settings.orm

        self.engine = create_async_engine(
            settings.orm.uri, 
            echo=settings.orm.engine_echo
        )

        self.sessionmaker = async_sessionmaker(
            autoflush=self.settings.session_autoflush, 
            autocommit=self.settings.session_autocommit, 
            expire_on_commit=self.settings.session_expire_on_commit
        )

class Application:
    def __init__(self, settings: Settings):
        self.orm = ObjectRelationalMapper(settings)
        
class Service:
    def __init__(self, bind: Application):
        self.bind = bind
        self.session = bind.orm.sessionmaker(bind=bind.orm.engine)
    
    async def begin(self):
        await self.session.begin()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()