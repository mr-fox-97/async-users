import asyncio
from datetime import timedelta
from typing import Dict, List, Callable
from collections import deque

from src.users.auth import exceptions
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

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


class Account(Entity): 
    def __init__(self, identity, handlers: Dict[Event, List[Callable]]):
        super().__init__(identity, handlers)
        self.__credential: Credential = None
        self.__access_token: Token = None

    @property
    def credential(self) -> Credential:
        return self.__credential
    
    @credential.setter
    def credential(self, credential: Credential):
        credential = Credential(account_id=self.id, username=credential.username, password=credential.password)
        if self.__credential:
            event = Event(type='credential-updated', payload=credential)
        else:
            event = Event(type='credential-added', payload=credential)
        self.__credential = credential
        self.events.append(event)

    async def authenticate(self, **kwargs):
        key, value = kwargs.popitem()
        if key == 'password':
            if not self.__credential:
                raise exceptions.InvalidCredentials
            
            if not self.__credential.verify(password=value):
                raise exceptions.InvalidPassword
        else:
            raise ValueError(f'Invalid key: {key}')
        
        event = Event(type='account-authenticated', payload=None)
        await self.handle(event)

    def access_token(self, expires_in: timedelta = timedelta(hours=8)) -> Token:
        claim = Claim(sub=self.id, exp=expires_in)
        return Tokenizer.encode(claim)
        