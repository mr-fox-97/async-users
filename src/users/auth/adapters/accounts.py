from uuid import uuid4
from typing import Dict, List, Callable
from sqlalchemy import insert, select, delete, update

from src.users.auth import exceptions
from src.users.auth.settings import Settings
from src.users.auth.schemas import  accounts
from src.users.auth.models.accounts import Account
from src.users.auth.adapters.credentials import Credentials

from src.users.settings import Settings
from src.users.repository import Repository

from src.users.auth.handlers import (
    AddCredential,
    UpdateCredential
)

class Accounts(Repository):
    def __init__(self, settings: Settings):
        super().__init__(settings)  
        self.credentials = Credentials(session=None)

        self.handlers: Dict[str, List[Callable]] = {
            'credential-added': [AddCredential(self.credentials)],
            'credential-updated': [UpdateCredential(self.credentials)],
            'account-authenticated': []
        }

    def initialize_attributes(self):
        self.credentials.session = self.session

    async def create(self, identity = uuid4()) -> Account:
        account = Account(identity, handlers=self.handlers)
        command = insert(accounts).values(id=account.id)
        await self.session.execute(command)
        return account
        
    async def read(self, **kwargs) -> Account:
        key, value = kwargs.popitem()
        if key == 'username':
            credential = await self.credentials.get(value)
            if not credential:
                raise exceptions.AccountNotFound(f'Account with username {value} not found')
            account = Account(identity=credential.account_id, handlers=self.handlers)
            account.credential = credential
        else:
            raise ValueError(f'Invalid key: {key}')
        return account
        
    async def delete(self, account: Account):
        command = delete(accounts).where(accounts.id == account.id)
        await self.session.execute(command)