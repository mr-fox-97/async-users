from uuid import UUID, uuid4
from dataclasses import dataclass

from src.users import exceptions
from src.domain import Repository, register
from src.users.ports.accounts import Accounts
from src.users.ports.emails import Emails
from src.users.ports.phones import Phones
from src.users.ports.credentials import Credentials
from src.users.aggregate import User

@dataclass
class Users(Repository[User]):
    accounts: Accounts
    emails: Emails
    phones: Phones
    credentials: Credentials

    @register.output
    async def create(self, name: str) -> User:
        account = await self.accounts.read(name)
        if account:
            raise exceptions.AccountAlreadyExists
        account = await self.accounts.create(name)
        return User(account)
    
    @register.output
    async def read(self, **kwargs) -> User:
        key, value = kwargs.popitem()
        if key == 'name' or key == 'username':
            account = await self.accounts.read(value)
        elif key == 'email':
            account = await self.emails.find(value)            
        elif key == 'phone':
            account = await self.phones.find(value)
        else:
            raise KeyError(f"Invalid key {key}")
        user = User(account)
        user.has_password = await self.credentials.check(user.account)
        return user
    
    @register.output
    async def find_by_username(self, username: str) -> User:
        account = await self.accounts.read(username)
        if not account:
            raise exceptions.AccountNotFound
        user = User(account)
        user.has_password = await self.credentials.check(user.account)
        return user
    
    @register.output
    async def find_by_email(self, email: str) -> User:
        account = await self.emails.find(email)
        if not account:
            raise exceptions.AccountNotFound
        user = User(account)
        user.has_password = await self.credentials.check(user.account)
        return user
    
    @register.output
    async def find_by_phone(self, phone: str) -> User:
        account = await self.phones.find(phone)
        if not account:
            raise exceptions.AccountNotFound
        user = User(account)
        user.has_password = await self.credentials.check(user.account)
        return user