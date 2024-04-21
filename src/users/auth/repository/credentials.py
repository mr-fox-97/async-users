from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.ports import DataAccessObject
from src.users.auth.schemas import  credentials
from src.users.auth.models.credentials import Credential

class Credentials(DataAccessObject):
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
    
    async def update(self, credential: Credential):
        command = update(credentials).where(credentials.account_id == credential.account_id).values(
            username=credential.username,
            password=credential.password.get_secret_value()
        )
        await self.session.execute(command)

    async def remove(self, credential: Credential):
        command = delete(credentials).where(credentials.account_id == credential.account_id)
        await self.session.execute(command)