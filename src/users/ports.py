from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Deque
from collections import deque
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from src.users.settings import Settings

from typing import Any
from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict

class Entity(ABC):
    def __init__(self, identity):
        self.__identity = identity
    
    @property
    def id(self):
        return self.__identity
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)

class Event(BaseModel):
    type: str = Field(..., description='Type of event')
    publisher: Entity = Field(default=None, description='Publisher of the event')
    timestamp: datetime = Field(default_factory=datetime.now, description='Timestamp of the event')
    payload: Any = Field(default=None, description='Payload of the event')
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Handler(ABC):
    @abstractmethod
    async def __call__(self, event: Event):
        ...

class Root(Entity):
    def __init__(self, __identity: Any, __handlers: Dict[str, List[Callable]] = {}):
        super().__init__( __identity)
        self.__handlers = __handlers
        self.__events: Deque[Event] = deque()
    
    def publish(self, event: Event):
        self.__events.append(Event(
            type=event.type,
            payload=event.payload,
            publisher=self
        ))
    
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

    def __setattr__(self, __name: str, __value: object) -> None:
        if hasattr(self, __name):
            attribute = getattr(self, __name)
            if attribute is None:
                if __value is not None:
                    self.publish(event = Event(type=f'{__name}-added', payload=__value))
            else:
                if __value is None:
                    self.publish(event = Event(type=f'{__name}-removed', payload=attribute))
                else:
                    self.publish(event = Event(type=f'{__name}-updated', payload=__value))
        return super().__setattr__(__name, __value)


class Schema(DeclarativeBase):
    pass

class DataAccessObject(ABC):
    def __init__(self, session):
        self.session = session

class UnitOfWork(ABC):
    def __init__(self, settings: Settings):
        self.__engine = create_async_engine(settings.database_uri, echo=settings.database_engine_echo)
        self.__session_factory = async_sessionmaker(
            autoflush=settings.database_session_autoflush,
            autocommit=settings.database_session_autocommit,
            expire_on_commit=settings.database_session_expire_on_commit
        )
        self.__testing_mode = settings.testing_mode
        self.__handlers = {}
    
    @property
    def handlers(self) -> Dict[str, List[Callable[[Event],None]]]:
        return self.__handlers

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