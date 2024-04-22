from typing import Optional
from typing import Tuple
from uuid import UUID

from sqlalchemy import insert, select, delete, update
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.ports import DataAccessObject, Schema
from src.users.auth.models.credentials import Credential
from src.users.auth.models.accounts import Account

class credentials(Schema):
    __tablename__ = 'credentials'
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey('accounts.id'))
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()


class Credentials(DataAccessObject):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, account: Account, credential: Credential):
        command = insert(credentials).values(
            account_id=account.id,
            username=credential.username,
            password=credential.password.get_secret_value()
        )
        await self.session.execute(command)
    
    async def update(self, account: Account, credential: Credential):
        command = update(credentials).where(credentials.account_id == account.id).values(
            username=credential.username,
            password=credential.password.get_secret_value()
        )
        await self.session.execute(command)

    async def remove(self, account: Account):
        command = delete(credentials).where(credentials.account_id == account.id)
        await self.session.execute(command)


    async def get(self, username: str) -> Optional[Tuple[UUID,Credential]]:
        result = await self.session.execute(
            select(credentials).where(credentials.username == username)
        )
        credential = result.scalars().first()
        if credential:
            identifier = credential.account_id
            return identifier, Credential(
                username=credential.username, 
                password=credential.password
            )
        return None