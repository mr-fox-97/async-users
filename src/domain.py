from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Protocol
from typing import TypeVar, Generic
from typing import List, Any

ID = TypeVar('ID')
@dataclass(kw_only=True, frozen=True)
class Entity(ABC, Generic[ID]):
    id: ID

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return value.id == self.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)

class Aggregate(Protocol):
    root: Entity

@dataclass(frozen=True)
class Event:
    name: str
    payload: Any
    publisher: Aggregate = None
    timestamp: datetime = datetime.now()
    id: UUID = uuid4()

@dataclass(frozen=True)
class Command:
    name: str
    payload: Any
    issuer: Aggregate = None


class Bus(ABC):
    @abstractmethod
    async def consume(self, event: Event):
        ...

    @abstractmethod
    async def execute(self, command: Command):
        ...

class Aggregate:
    def __init__(self):
        self.events: List[Event]
        self.bus: Bus

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.events = list()
        return instance
    
    @property
    @abstractmethod
    def root(self) -> Entity:
        ...

    async def execute(self, command: Command):
        return await self.bus.execute(command)

    def publish(self, event: Event):
        self.events.append(event)

    async def dispatch(self, event: Event):
        await self.bus.consume(event)

    async def save(self):
        for event in self.events:
            await self.bus.consume(event)
        self.events.clear()