from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from src.users.settings import Settings

class Repository(ABC):
    def __init__(self, settings: Settings):
        self.__engine = create_async_engine(settings.database_uri, echo=settings.database_engine_echo)
        self.__session_factory = async_sessionmaker(
            autoflush=settings.database_session_autoflush,
            autocommit=settings.database_session_autocommit,
            expire_on_commit=settings.database_session_expire_on_commit
        )
        self.__testing_mode = settings.testing_mode

    @abstractmethod
    def initialize_attributes(self):
        ...

    async def begin(self):
        self.__connection = await self.__engine.connect()
        self.__transaction = await self.__connection.begin()
        self.session = self.__session_factory(bind=self.__connection)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def __aenter__(self):       
        await self.begin()
        self.initialize_attributes()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__testing_mode is True or exc_type is not None:
            await self.__transaction.rollback()
        else:
            await self.__transaction.commit()
        await self.__connection.close()