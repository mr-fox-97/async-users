from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, List, Callable

from sqlalchemy import insert, delete, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.settings import Settings
from src.users.ports import UnitOfWork, Schema, Event
from src.users.auth import handlers
from src.users.auth import exceptions
from src.users.auth.models.accounts import Account
from src.users.auth.repository.credentials import Credentials

class accounts(Schema):
    __tablename__ = 'accounts'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

class Accounts(UnitOfWork):
    def __init__(self, settings: Settings):
        super().__init__(settings)  
        self.credentials = Credentials(session=None)
        self.handlers['account-created'] = [self.handle_account_creation]
        self.handlers['account-deleted'] = [self.handle_account_deletion]
        self.handlers['credential-added'] = [handlers.AddCredential(self.credentials)]
        self.handlers['credential-updated'] = [handlers.UpdateCredential(self.credentials)]
        self.handlers['credential-removed'] = [handlers.RemoveCredential(self.credentials)]

    async def create(self) -> Account:
        identity = uuid4()
        command = insert(accounts).values(id=identity)
        result = await self.session.execute(command)
        account = Account(
            identity=result.inserted_primary_key[0], 
            handlers=self.handlers
        )
        account.publish(event = Event(type='account-created'))
        return account
    
    async def read(self, **kwargs) -> Account:
        key, value = kwargs.popitem()
        if key == 'username':
            identifier, credential = await self.credentials.get(value)
            if not identifier:
                raise exceptions.AccountNotFound(f'Account with username {value} not found')
            account = Account(identity=identifier, handlers=self.handlers, credential=credential)
            
        else:
            raise ValueError(f'Invalid key: {key}')
        return account
    
    async def handle_account_deletion(self, event: Event):
        command = delete(accounts).where(accounts.id == event.publisher.id)
        await self.session.execute(command)
    
    async def handle_account_creation(self, event: Event):
        print(f'Account created: {event.publisher}')