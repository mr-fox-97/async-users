import pytest
from src.users.services import Users
from src.services import Application
from src.adapters import UnitOfWork as UOW

@pytest.fixture
def application(settings) -> Application:
    return Application(settings)

@pytest.fixture
def users(application: Application, uow: UOW):
    users = Users(bind=application)
    users.session = uow.session
    users.repository.accounts.session = uow.session
    users.repository.emails.session = uow.session
    users.repository.phones.session = uow.session
    users.repository.credentials.session = uow.session
    return users

@pytest.mark.asyncio
async def test_users_service(users: Users): 

    async with users:
        user = await users.create('user')
        assert user.has_password is False

        user.password = 'password'
        await user.save()
    
    async with users:
        with pytest.raises(Exception):
            user =await users.create('user')

    async with users:
        user = await users.read('user')
        assert user.account.id
        assert user.has_password is True
        assert await user.verify('password') is True
        assert await user.verify('wrong') is False
        user.password = 'new-password'
        await user.save()

    async with users:
        user = await users.read('user')
        assert await user.verify('new-password') is True
        assert await user.verify('password') is False
        user.password = None
        await user.save()

    async with users:
        user = await users.read('user')
        assert user.has_password is False
        assert await user.verify('new-password') is False
        assert await user.verify('password') is False
        await user.save()



