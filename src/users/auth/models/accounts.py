import asyncio
from datetime import timedelta
from typing import Dict, List, Callable
from collections import deque

from src.users.auth import exceptions
from src.users.ports import Event, Entity
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

class Account(Entity): 
    def __init__(self, identity, handlers: Dict[Event, List[Callable]]):
        super().__init__(identity, handlers)
        self.__credential: Credential = None

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