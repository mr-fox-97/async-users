from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from typing import Optional

from src.adapters import DataAccessObject as DAO
from src.users.models import Account, Credential

class Credentials(ABC, DAO):
    
    @abstractmethod
    async def add(self, account: Account, credential: Credential):
        ...

    @abstractmethod
    async def verify(self, account: Account, credential: Credential) -> bool:
        ...
            
    @abstractmethod
    async def update(self, account: Account, credential: Credential):
        ...

    @abstractmethod
    async def check(self, account: Account) -> bool:
        ...

    @abstractmethod
    async def remove(self, account: Account):
        ...