from typing import Optional
from uuid import UUID

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.users.auth import exceptions
from src.users.auth.settings import Settings
from src.users.auth.schemas import  accounts, credentials
from src.users.auth.models.accounts import Account
from src.users.auth.models.credentials import Credential


class Credentials:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, credential: Credential):
        command = insert(credentials).values(
            account_id=credential.account_id,
            username=credential.username,
            password=credential.password.get_secret_value()
        )
        await self.session.execute(command)

    async def get(self, username: str) -> Optional[Credential]:
        result = await self.session.execute(
            select(credentials).where(credentials.username == username)
        )
        credential = result.scalars().first()
        return Credential(
            account_id=credential.account_id,
            username=credential.username,
            password=credential.password
        ) if credential else None


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
            account = Account(identity=credential.account_id)
            account.credential = credential
            return account
        else:
            raise ValueError(f'Invalid key: {key}')