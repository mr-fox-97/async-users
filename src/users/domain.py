import functools
from uuid import UUID, uuid4
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from typing import Any
from typing import Dict, Callable, List
from datetime import datetime
from dataclasses import dataclass
from queue import Queue

ID = TypeVar('ID')
class Entity(ABC, Generic[ID]):

    @property
    @abstractmethod
    def id(self) -> ID:
        ...

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return value.id == self.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Command:
    name: str
    payload: Any
    issuer: Entity = None

@dataclass
class Event:
    name: str
    payload: Any
    producer: Entity = None
    timestamp: datetime = datetime.now()
    id: UUID = uuid4()

class Aggregate:
    def __init__(self):
        self.is_registered = False
        self.queue: Queue = None
        self.tasks: List[Command] = []
        self.events: List[Event] = []
        self.handlers: Dict[str, List[Callable[[Command], None]]] = {}

    def publish(self, event: Event):
        self.queue.put(event)

    def subscribe(self, tag: str, handler: Callable[[Command], None]):
        if tag not in self.handlers:
            self.handlers[tag] = []
        self.handlers[tag].append(handler)

    async def save(self):
        for task in self.tasks:
            await self.execute(task)
        self.tasks.clear()

        for event in self.events:
            self.publish(event)

    async def execute(self, command: Command):
        if command.name in self.handlers:
            for handler in self.handlers[command.name]:
                await handler(command)
        else:
            raise Exception(f"Command handler not found: {command.name}")
        
        
T = TypeVar('T', bound=Aggregate)
class Repository(ABC, Generic[T]):
    
    @property
    @abstractmethod
    def queue(self) -> Queue:
        ...

    @property
    @abstractmethod
    def handlers(self) -> Dict[str, List[Callable[[Command], None]]]:
        ...


def register(method):
    @functools.wraps(method)
    async def wrapper(self: Repository, *args, **kwargs):
        aggregate: Aggregate = await method(self, *args, **kwargs)
        aggregate.queue = self.queue
        for key, value in self.handlers.items():
            for handler in value:
                aggregate.is_registered = True
                aggregate.subscribe(key, handler)
        return aggregate
    return wrapper