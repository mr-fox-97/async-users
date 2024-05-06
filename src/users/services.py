from uuid import uuid4, UUID

from src.users import exceptions
from src.users.repository import Repository
from src.users.adapters.accounts import Accounts
from src.users.adapters.credentials import Credentials
from src.users.adapters.emails import Emails
from src.users.adapters.phones import Phones
from src.users.aggregate import User, Event
from src.services import Application, Service, register

class Users(Service):
    def __init__(self, bind: Application):
        super().__init__(bind)

        self.repository = Repository(
            accounts=Accounts(self.session),
            emails=Emails(self.session),
            phones=Phones(self.session),
            credentials=Credentials(self.session)
        )

        self.subscribe('user-created', lambda event: self.repository.add(event.payload))
        self.subscribe('password-created', lambda event: self.repository.credentials.add(event.publisher.root, event.payload))
        self.subscribe('password-updated', lambda event: self.repository.credentials.update(event.publisher.root, event.payload))
        self.subscribe('password-removed', lambda event: self.repository.credentials.remove(event.publisher.root))
        self.register('verify-password', lambda command: self.repository.credentials.verify(command.issuer.root, command.payload))
    
    @register
    async def create(self, name: str, id: UUID = None):
        user = await self.repository.get_by_name(name)
        if user is not None:
            raise exceptions.AccountAlreadyExists(f"Account with name '{name}' already exists")
        user = User(name=name, id=id or uuid4())
        user.publish(event=Event('user-created', payload=user))
        return user
    
    @register
    async def read(self, name: str):
        user = await self.repository.get_by_name(name)
        if user is None:
            raise exceptions.AccountNotFound(f"Account with name '{name}' not found")
        return user