from typing import Dict, Callable, Any, List
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from src.domain import Command, Event
from src.settings import Settings

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

class Bus:
    def __init__(self):
        self.handlers: Dict[str, Callable[[Command], Any]] = {}
        self.consumers: Dict[str, List[Callable[[Event], None]]] = {}

    async def consume(self, event: Event):
        for consumer in self.consumers.get(event.name, []):
            await consumer(event)
    
    async def execute(self, command: Command):
        return await self.handlers[command.name](command)


class Application:
    def __init__(self, settings: Settings):
        self.orm = ObjectRelationalMapper(settings)
        self.bus = Bus()


class Service:
    def __init__(self, bind: Application):
        self.bus = bind.bus
        self.session = bind.orm.sessionmaker(bind=bind.orm.engine)

    def subscribe(self, name: str, consumer: Callable[[Event], None]):
        self.bus.consumers.setdefault(name, []).append(consumer)
    
    def register(self, name: str, handler: Callable[[Command], Any]):
        self.bus.handlers[name] = handler
    
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

import functools

def register(method):
    @functools.wraps(method)
    async def wrapper(self: Service, *args, **kwargs):
        aggregate = await method(self, *args, **kwargs)
        setattr(aggregate, 'bus', self.bus)
        return aggregate
    return wrapper