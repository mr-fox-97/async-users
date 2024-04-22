from dataclasses import dataclass
from datetime import timedelta

from src.users.auth import exceptions
from src.users.ports import Event, Root
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

class Account(Root): 
    def __init__(self, identity, handlers = {}, credential: Credential = None):
        super().__init__(identity, handlers)
        self.credential = credential

    async def authenticate(self, **kwargs):
        key, value = kwargs.popitem()
        if key == 'password':
            if not self.credential:
                raise exceptions.InvalidCredentials
            
            if not self.credential.verify(password=value):
                raise exceptions.InvalidPassword
        else:
            raise ValueError(f'Invalid key: {key}')
        
        event = Event(type='account-authenticated',publisher=self.id , payload=None)
        await self.handle(event)

    def access_token(self, expires_in: timedelta = timedelta(hours=8)) -> Token:
        claim = Claim(sub=self.id, exp=expires_in)
        return Tokenizer.encode(claim)