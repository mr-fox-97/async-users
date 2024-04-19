from uuid import uuid4

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.users.auth import exceptions
from src.users.auth.settings import Settings
from src.users.auth.schemas import  accounts
from src.users.auth.models.accounts import Account
from src.users.auth.models.credentials import Credential
from src.users.auth.adapters.credentials import Credentials

from typing import TypeVar, Generic
from typing import Set, Dict, List
from typing import Callable
from typing import Generator
from collections import deque

from src.users.auth.models import events
from src.users.auth.models.events import Event

class Accounts:
    def __init__(self, settings: Settings):
        self.__engine = create_async_engine(settings.database_uri, echo=settings.database_engine_echo)
        self.__session_factory = async_sessionmaker(
            autoflush=settings.database_session_autoflush,
            autocommit=settings.database_session_autocommit,
            expire_on_commit=settings.database_session_expire_on_commit
        )
        self.__testing_mode = settings.testing_mode

    async def begin(self):
        self.__connection = await self.__engine.connect()
        self.__transaction = await self.__connection.begin()
        self.session = self.__session_factory(bind=self.__connection)
        await self.session.begin()
        self.credentials = Credentials(session=self.session)

    async def close(self):
        await self.session.close()
        await self.__transaction.rollback()
        await self.__connection.close()

    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()

    async def __aenter__(self):
        await self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__testing_mode is True or exc_type is not None:
            await self.__transaction.rollback()
        else:
            await self.__transaction.commit()
        await self.__connection.close()

    async def add(self, account: Account):
        command = insert(accounts).values(id=account.id)
        await self.session.execute(command)

    async def delete(self, account: Account):
        command = delete(accounts).where(accounts.id == account.id)
        await self.session.execute(command)

    async def read(self, **kwargs) -> Account:
        key, value = kwargs.popitem()
        if key == 'username':
            credential = await self.credentials.get(value)
            if credential is None:
                raise exceptions.AccountNotFound(f'Account with username {value} not found')
            account = Account(identity=credential.account_id)
            account.credential = credential
            return account
        else:
            raise ValueError(f'Invalid key: {key}')
        
    async def create(self, username: str, password: str) -> Account:
        account = Account(identity=uuid4())
        account.credential = Credential(account_id=account.id, username=username, password=password)
        await self.add(account)
        await self.credentials.add(account.credential)
        return account