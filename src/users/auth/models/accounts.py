import asyncio
from uuid import uuid4
from datetime import timedelta
from typing import Any, Dict, List, Callable
from collections import deque

from pydantic.dataclasses import dataclass
from pydantic import Field

from src.users.auth import exceptions
from src.users.ports import Event, Entity
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

@dataclass
class Attributes:
    identity: Any = Field(default_factory=uuid4)
    handlers: Dict[str, List[Callable]] = Field(default={})
    events: List[Event] = Field(default={})
    credential: Credential = Field(default=None)

class Account(Entity): 
    def __init__(self, attributes: Attributes):
        super().__init__(attributes.identity, attributes.handlers, attributes.events)
        self.__credential: Credential = attributes.credential

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