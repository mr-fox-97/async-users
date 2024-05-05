from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from typing import Optional, List

from src.adapters import DataAccessObject as DAO
from src.users.models import Account, Email

class Emails(ABC, DAO):

    @abstractmethod
    async def add(self, account: Account, email: Email):
        ...

    @abstractmethod
    async def remove(self, email: Email):
        ...

    @abstractmethod
    async def get(self, account: Account) -> List[Email]:
        ...

    @abstractmethod
    async def clear(self, account: Account):
        ...

    @abstractmethod
    async def find(self, address: str) -> Optional[Account]:
        ...
