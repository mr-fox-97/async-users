from abc import ABC, abstractmethod
from typing import Dict, List, Callable
from collections import deque

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from src.users.settings import Settings

from typing import Any
from pydantic import BaseModel
from pydantic import Field


class Event(BaseModel):
    type: str = Field(..., alias='type')
    payload: Any = Field(..., alias='payload')


class Entity:
    def __init__(self, identity, handlers: Dict[Event, List[Callable]] = {}, events: List[Event] = []):
        self.__identity = identity
        self.__handlers = handlers
        self.__events = deque(events)

    @property
    def id(self):
        return self.__identity
    
    @property
    def events(self):
        return self.__events
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)
        
    async def handle(self, event: Event):
        for __handler in self.__handlers.get(event.type, []):
            await __handler(event)

    async def save(self):
        while self.__events:
            event = self.__events.popleft()
            for __handler in self.__handlers[event.type]:
                await __handler(event)

    def discard(self):
        self.__events.clear()


class DataAccessObject(ABC):
    def __init__(self, session):
        self.session = session


class Repository(ABC):
    def __init__(self, settings: Settings):
        self.__engine = create_async_engine(settings.database_uri, echo=settings.database_engine_echo)
        self.__session_factory = async_sessionmaker(
            autoflush=settings.database_session_autoflush,
            autocommit=settings.database_session_autocommit,
            expire_on_commit=settings.database_session_expire_on_commit
        )
        self.__testing_mode = settings.testing_mode

    def initialize_attributes(self):
        for attribute in self.__dict__.values():
            if isinstance(attribute, DataAccessObject):
                attribute.session = self.session

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