from src.users.ports import Event, Handler
from src.users.auth import events
from src.users.auth import exceptions
from src.users.auth.repository.credentials import Credentials

class AddCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialAdded):
        await self.credentials.add(account=event.publisher, credential=event.payload)

class UpdateCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialUpdated):
        await self.credentials.update(account=event.publisher, credential=event.payload)

class RemoveCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialRemoved):
        await self.credentials.remove(account=event.publisher)