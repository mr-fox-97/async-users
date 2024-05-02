from uuid import uuid4, UUID
from typing import Optional

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker ,AsyncSession

from src.users.adapters import DataAccessObject as DAO
from src.users.auth.models import Account
from src.users.auth.schemas import accounts
from src.users.auth.adapters.credentials import Credentials
from src.users.auth.adapters.emails import Emails
from src.users.auth.adapters.phones import Phones

class Accounts(DAO):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        super().__init__(sessionmaker)
        self.credentials = Credentials(session = self.session)
        self.emails = Emails(session = self.session)
        self.phones = Phones(session = self.session)

    async def create(self, username: str, userid: UUID = uuid4()) -> Account:
        command = insert(accounts).values(user_id=userid, user_name=username)
        result = await self.session.execute(command)
        return Account(id=result.inserted_primary_key[0], user_id=userid, username=username)
    
    async def read(self, username: str) -> Optional[Account]:
        query = select(accounts).where(accounts.user_name == username)
        result = await self.session.execute(query)
        record = result.scalars().first()
        return Account(id=record.id, user_id=record.user_id, username=record.user_name) if record else None
    
    async def update(self, account: Account):
        command = update(accounts).where(accounts.user_name == account.username).values(id=account.id)
        await self.session.execute(command)

    async def delete(self, account: Account):
        command = delete(accounts).where(accounts.id == account.id)
        await self.session.execute(command)
    
    async def get(self, userid: UUID) -> Optional[Account]:
        query = select(accounts).where(accounts.user_id == userid)
        result = await self.session.execute(query)
        record = result.scalars().first()
        return Account(id=record.id, user_id=record.user_id, username=record.user_name) if record else None