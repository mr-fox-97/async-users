from abc import ABC, abstractmethod
from typing import Optional, List

from src.adapters import DataAccessObject as DAO
from src.users.models import Account, Phone

class Phones(ABC, DAO):

    @abstractmethod
    async def add(self, account: Account, phone: Phone):
        ...

    @abstractmethod
    async def remove(self, phone: Phone):
        ...

    @abstractmethod
    async def get(self, account: Account) -> List[Phone]:
        ...

    @abstractmethod
    async def clear(self, account: Account):
        ...

    @abstractmethod
    async def find(self, number: str) -> Optional[Account]:
        ...