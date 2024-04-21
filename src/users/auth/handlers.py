from src.users.ports import Event, Handler
from src.users.auth import events
from src.users.auth import exceptions
from src.users.auth.repository.credentials import Credentials

class AddCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialAdded):
        credential = event.payload
        await self.credentials.add(credential)

class UpdateCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialUpdated):
        credential = event.payload
        await self.credentials.update(credential)

class RemoveCredential(Handler):
    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    async def __call__(self, event: events.CredentialRemoved):
        credential = event.payload
        await self.credentials.remove(credential)