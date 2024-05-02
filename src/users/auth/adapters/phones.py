from typing import List
from typing import Optional
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.users.adapters import DataAccessObject
from src.users.auth.models import Phone, Account
from src.users.auth.schemas import phones, accounts

class Phones:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, account: Account, phone: Phone):
        command = insert(phones).values(
            account_id=account.id,
            phone_number=phone.number,
            phone_is_verified=phone.is_verified,
            phone_is_primary=phone.is_primary
        )
        await self.session.execute(command)

    async def clear(self, account: Account):
        command = delete(phones).where(phones.account_id == account.id)
        await self.session.execute(command)

    async def remove(self, phone: Phone):
        command = delete(phones).where(phones.id == phone.id)
        await self.session.execute(command)
            
    async def get(self, account: Account) -> List[Phone]:
            query = select(phones).where(phones.account_id == account.id)
            result = await self.session.execute(query)
            records = result.scalars().all()
            return [Phone(
                id=record.id,
                number=record.phone_number, 
                is_verified=record.phone_is_verified, 
                is_primary=record.phone_is_primary
            ) for record in records]
    
    async def find(self, number: str) -> Optional[Account]:
            query = select(accounts).join(phones).where(phones.phone_number == number)
            result = await self.session.execute(query)
            record = result.scalars().first()
            return Account(id=record.id, user_id=record.user_id, username=record.user_name) if record else None