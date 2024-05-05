from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey

class DatabaseSchema(DeclarativeBase):
    pass

class accounts(DatabaseSchema):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column()
    user_name: Mapped[str] = mapped_column(unique=True)

class credentials(DatabaseSchema):
    __tablename__ = 'credentials'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    password_hash: Mapped[str] = mapped_column(nullable=False)
    password_salt: Mapped[str] = mapped_column(nullable=True)

class emails(DatabaseSchema):
    __tablename__ = 'emails'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    email_address: Mapped[str] = mapped_column(unique=True)
    email_is_primary: Mapped[bool] = mapped_column(default=False)
    email_is_verified: Mapped[bool] = mapped_column(default=False)

class phones(DatabaseSchema):
    __tablename__ = 'phones'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    phone_number: Mapped[str] = mapped_column(unique=True)
    phone_is_primary: Mapped[bool] = mapped_column(default=False)
    phone_is_verified: Mapped[bool] = mapped_column(default=False)