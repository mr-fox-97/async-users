import pytest
from src.users.services import Users
from src.domain import Event
from src.adapters import UnitOfWork as UOW
from src.services import Application
from src.users.adapters.accounts import Accounts
from src.users.adapters.credentials import Credentials
from src.users.adapters.emails import Emails
from src.users.adapters.phones import Phones

@pytest.fixture(scope='function')
async def users(settings, uow: UOW):
    application = Application(settings)
    users = Users(bind=application)
    users.accounts = Accounts(uow.session)
    users.emails = Emails(uow.session)
    users.phones = Phones(uow.session)
    users.credentials = Credentials(uow.session)
    return users

@pytest.mark.asyncio
async def test_verify_password(users: Users):
    async with users:
        user = await users.create(name='test')
        assert user.has_password == False
        user.password = 'password'
        await user.save()

    async with users:
        user = await users.read(name='test')        
        assert user.has_password == True
        assert await user.verify('password') == True
        assert await user.verify('invalid') == False
