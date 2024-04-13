from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

class schema(DeclarativeBase):
    pass

class accounts(schema):
    __tablename__ = 'accounts'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()

class credentials(schema):
    __tablename__ = 'credentials'
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey('accounts.id'))
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()