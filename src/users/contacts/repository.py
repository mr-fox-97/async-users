from typing import List
from typing import Tuple
from datetime import datetime

from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

from src.users.ports import DataAccessObject, Schema
from src.users.models import User

class Contact(BaseModel):
    id: int
    user_id: int
    name: str

class contacts(Schema):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    contact_id: Mapped[int] = mapped_column()

class Contacts(DataAccessObject):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, identifier: int, contact: Contact):
        command = insert(contacts).values(
            user_id=contact.user_id,
            contact_id=contact.id
        )
        await self.session.execute(command)

    async def get(self, identifier: int) -> List[Contact]:
        result = await self.session.execute(
            select(contacts).where(contacts.user_id == identifier)
        )
        return [Contact(id=contact.contact_id) for contact in result.scalars()]
    
    async def remove(self, identifier: int, contact: Contact):
        command = delete(contacts).where(contact.user_id == identifier, contacts.contact_id == contact.id)
        await self.session.execute(command)


class Messages(DataAccessObject):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, user: User, contact: Contact) -> List[Message]:
        result = await self.session.execute(
            select(messages).where(messages.user_id == identifier, messages.contact_id == contact.id)
        )
        return [Message(id=message.id, user_id=message.user_id, contact_id=message.contact_id, content=message.content) for message in result.scalars()]