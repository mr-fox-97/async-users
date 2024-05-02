from uuid import UUID
from dataclasses import dataclass
import random, string

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.auth.schemas import credentials
from src.users.auth.models import Credential, Security, Account

def random_salt(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

class Credentials:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, account: Account, credential: Credential):
        salt = random_salt(22)
        command = insert(credentials).values(
            account_id=account.id, 
            password_hash=Security.hash(credential.password).get_secret_value(),
            password_salt=salt
        )
        await self.session.execute(command)

    async def verify(self, account: Account, credential: Credential) -> bool:
        query = select(credentials).where(credentials.account_id == account.id)
        result = await self.session.execute(query)
        record = result.scalars().first()
        return Security.verify(
            password=credential.password.get_secret_value(), 
            hash=record.password_hash, 
        ) if record else False
            
    async def update(self, account: Account, credential: Credential):
        salt = random_salt(22)
        command = update(credentials).where(credentials.account_id == account.id).values(
            password_hash=Security.hash(credential.password).get_secret_value(),
            password_salt=salt
        )
        await self.session.execute(command)

    async def check(self, account: Account) -> bool:
        query = select(credentials).where(credentials.account_id == account.id)
        result = await self.session.execute(query)
        return result.scalars().first() is not None
        
    async def remove(self, account: Account):
        command = delete(credentials).where(credentials.account_id == account.id)
        await self.session.execute(command)