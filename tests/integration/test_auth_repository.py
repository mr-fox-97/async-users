import pytest
from typing import AsyncGenerator
from src.users.services import Application
from src.users.adapters import ObjectRelationalMapper as ORM
from src.users.auth.adapters.accounts import Accounts
from src.users.auth.models import Email, Credential, Phone
from src.users.auth.repository import Users
from src.users.auth.aggregate import User

@pytest.fixture(scope='function')
async def users(application: Application, sessionmaker: AsyncGenerator) -> Users:
    users = Users(application)
    users.session = sessionmaker
    users.accounts.__init__(sessionmaker)
    return users

@pytest.mark.asyncio
async def test_users(users: Users):   
    async with users:
        accounts = users.accounts
        async with accounts:
            account = await users.accounts.create(username='test')
            await users.accounts.credentials.add(account, Credential(password='test'))
            await users.accounts.emails.add(account, Email(address='test@test.com'))
            await users.accounts.phones.add(account, Phone(number='1234567890'))
            await users.accounts.phones.add(account, Phone(number='1234567890'))

        user = await users.read(username='test')
        assert user.id == account.user_id
        assert user.name == account.username