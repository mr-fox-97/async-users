from uuid import UUID, uuid4

from src.users.adapters import UnitOfWork
from src.users.domain import Repository, register
from src.users.auth import exceptions
from src.users.auth.aggregate import User
from src.users.auth.adapters.accounts import Accounts
from src.users.services import Application

from queue import Queue

class Users(UnitOfWork, Repository[User]):
    def __init__(self, bind: Application):
        super().__init__(bind.orm.engine, bind.orm.sessionmaker)
        self.accounts = Accounts(self.session)

    @property
    def handlers(self):
        return {}
    
    @property
    def queue(self):
        return Queue()
    
    @register
    async def create(self, name: str, id: UUID = uuid4()) -> User:
        async with self.accounts:
            account = await self.accounts.create(name, id)
            return User(account)
        
    @register
    async def read(self, **kwargs) -> User:
        async with self.accounts:
            key, value = kwargs.popitem()
            if key == 'username' or key == 'name':
                account = await self.accounts.read(username=value)
            elif key == 'email':
                account = await self.accounts.emails.find(value)
            elif key == 'phone':
                account = await self.accounts.phones.find(value)
            else:
                raise KeyError(f'Invalid key: {key}')
            
            if not account:
                raise exceptions.AccountNotFound(f'Account with {key} {value} not found')
            
            user = User(account)
            user.emails = await self.accounts.emails.get(account)
            user.phones = await self.accounts.phones.get(account)
            user.has_password = await self.accounts.credentials.check(account)
            return user
    
    @register
    async def get(self, id: UUID) -> User:
        async with self.accounts:
            account = await self.accounts.get(id)
            if not account:
                raise exceptions.AccountNotFound(f'Account not found')
            
            user = User(account)
            user.emails = await self.accounts.emails.get(account)
            user.phones = await self.accounts.phones.get(account)
            user.has_password = await self.accounts.credentials.check(account)
            return user