from uuid import uuid4, UUID
from typing import Optional

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.ports.accounts import Accounts as DAO
from src.users.models import Account
from src.users.schemas import accounts

class Accounts(DAO):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        command = update(accounts).where(accounts.id == account.id).values(
            user_id=account.user_id,
            user_name=account.username
        )
        await self.session.execute(command)

    async def delete(self, account: Account):
        command = delete(accounts).where(accounts.id == account.id)
        await self.session.execute(command)