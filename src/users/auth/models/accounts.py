from uuid import UUID
from typing import Protocol
from pydantic import SecretStr

class Credential(Protocol):
    username: str
    password: SecretStr

    def verify(self, secret: SecretStr) -> bool:
        ...

class Account:
    def __init__(self, identity):
        self.identity = identity
        self.credential: Credential = None

    @property
    def id(self):
        return self.identity
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)