from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from typing import Optional

from src.adapters import DataAccessObject as DAO
from src.users.models import Account

class Accounts(ABC, DAO):

    @abstractmethod
    async def create(self, username: str, userid: UUID = uuid4()) -> Account:
        ...
    
    @abstractmethod
    async def read(self, username: str) -> Optional[Account]:
        ...
    
    @abstractmethod
    async def update(self, account: Account):
        ...

    @abstractmethod
    async def delete(self, account: Account):
        ...