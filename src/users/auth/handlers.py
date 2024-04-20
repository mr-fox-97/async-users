from abc import ABC, abstractmethod

from src.users.auth.models.accounts import Event
from src.users.auth.repository.credentials import Credentials

class Handler(ABC):
    @abstractmethod
    async def __call__(self, event: Event):
        ...

class AddCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: Event):
        credential = event.payload
        await self.credentials.add(credential)

class UpdateCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: Event):
        credential = event.payload
        await self.credentials.update(credential)