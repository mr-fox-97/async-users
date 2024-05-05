import functools
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC
from queue import Queue
from typing import TypeVar, Generic
from typing import List, Any
from typing import Set
from typing import Dict
from typing import Callable

ID = TypeVar('ID')
class Entity(ABC, Generic[ID]):

    def __init__(self, id: ID):
        self.id = id
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == 'id' and hasattr(self, 'id'):
            raise AttributeError('Entity id is immutable')
        return super().__setattr__(name, value)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, self.__class__):
            return value.id == self.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Event:
    name: str
    payload: Any
    publisher: Entity = None
    timestamp: datetime = datetime.now()
    id: UUID = uuid4()

@dataclass
class Command:
    name: str
    payload: Any
    issuer: Entity = None

@dataclass
class Root:
    def __init__(self):
        self.events: List[Event]
        self.tasks: List[Command]
        self.handlers: Dict[str, Callable[[Command], Any]]

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.events = []
        instance.tasks = []
        instance.handlers = {}
        return instance
    
    async def execute(self, command: Command) -> Any:
        handler = self.handlers.get(command.name)
        if handler:
            return await handler(command)
        else:
            raise AttributeError(f'Command handler for {command.name} not found')
        
    async def save(self):
        for task in self.tasks:
            await self.execute(task)
        self.tasks.clear()
        

T = TypeVar('T', bound=Root)
class Repository(ABC, Generic[T]):
    def __init__(self):
        self.collection: Set[T]
        self.handlers: Dict[str, Callable[[Command], Any]]
    
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.collection = set()
        instance.handlers = {}
        return instance


class register:
    @staticmethod
    def output(method):
        @functools.wraps(method)
        async def wrapper(self: Repository, *args, **kwargs):
            aggregate: Root = await method(self, *args, **kwargs)
            aggregate.handlers = self.handlers
            self.collection.add(aggregate)
            return aggregate
        return wrapper