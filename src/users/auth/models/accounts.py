from uuid import UUID
from datetime import timedelta
from typing import Protocol
from typing import Union
from pydantic import SecretStr

from src.users.auth import exceptions
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

class Credential(Protocol):
    def verify(self, secret: SecretStr) -> bool:
        ...

class Account:
    def __init__(self, identity):
        self.identity = identity
        self.credential: Credential = None

    @property
    def id(self):
        return self.identity
    
    def authenticate(self, secret: Union[str, SecretStr], expiration: timedelta = timedelta(days=1)) -> Token:
        if self.credential.verify(secret):
            return Tokenizer.encode(claim=Claim(sub=self.id, exp=expiration))
        else:
            raise exceptions.InvalidCredentials("Invalid credentials")
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)