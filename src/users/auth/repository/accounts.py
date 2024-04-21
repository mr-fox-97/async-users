from uuid import uuid4
from typing import Dict, List, Callable

from sqlalchemy import insert, select, delete, update

from src.users.settings import Settings
from src.users.ports import Repository
from src.users.auth import handlers
from src.users.auth import exceptions
from src.users.auth.schemas import  accounts
from src.users.auth.models.credentials import Credential
from src.users.auth.models.accounts import Account, Attributes
from src.users.auth.repository.credentials import Credentials

class Accounts(Repository):
    def __init__(self, settings: Settings):
        super().__init__(settings)  
        self.credentials = Credentials(session=None)
        self.__handlers = {
            'credential-added': [handlers.AddCredential(self.credentials)],
            'credential-updated': [handlers.UpdateCredential(self.credentials)],
            'credential-removed': [handlers.RemoveCredential(self.credentials)],
        }

    @property
    def handlers(self) -> Dict[str, List[Callable]]:
        return self.__handlers

    async def create(self) -> Account:
        account = Account(attributes=Attributes(
            identity= uuid4(), 
            handlers=self.handlers, 
        ))
        command = insert(accounts).values(id=account.id)
        await self.session.execute(command)
        return account
        
    async def read(self, **kwargs) -> Account:
        key, value = kwargs.popitem()
        if key == 'username':
            credential = await self.credentials.get(value)
            if not credential:
                raise exceptions.AccountNotFound(f'Account with username {value} not found')
            
            account = Account(attributes=Attributes(
                identity=credential.account_id, 
                handlers=self.handlers, 
                credential=credential
            ))
            
        else:
            raise ValueError(f'Invalid key: {key}')
        return account
        
    async def delete(self, account: Account):
        command = delete(accounts).where(accounts.id == account.id)
        await self.session.execute(command)
        del account