from typing import List
from typing import Optional
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.users.ports.emails import Emails as DAO
from src.users.models import Email, Account
from src.users.schemas import emails, accounts

class Emails(DAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, account: Account, email: Email):
        command = insert(emails).values(
            account_id=account.id,
            email_address=email.address,
            email_is_verified=email.is_verified,
            email_is_primary=email.is_primary
        )
        await self.session.execute(command)
    
    async def remove(self, email: Email):
        command = delete(emails).where(emails.email_address == email.address)
        await self.session.execute(command)

    async def get(self, account: Account) -> List[Email]:
        query = select(emails).where(emails.account_id == account.id)
        result = await self.session.execute(query)
        records = result.scalars().all()
        return [Email(
            id=record.id,
            address=record.email_address, 
            is_verified=record.email_is_verified, 
            is_primary=record.email_is_primary
        ) for record in records]
    
    async def clear(self, account: Account):
        command = delete(emails).where(emails.account_id == account.id)
        await self.session.execute(command)

    async def find(self, address: str) -> Optional[Account]:
        query = select(accounts).join(emails).where(emails.email_address == address)
        result = await self.session.execute(query)
        record = result.scalars().first()
        return Account(id=record.id, user_id=record.user_id, username=record.user_name) if record else None