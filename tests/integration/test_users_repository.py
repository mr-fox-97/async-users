import pytest

from src.adapters import UnitOfWork as UOW
from src.domain import Event
from src.users.adapters.accounts import Accounts
from src.users.adapters.credentials import Credentials
from src.users.adapters.emails import Emails
from src.users.adapters.phones import Phones
from src.users.repository import Users

@pytest.mark.asyncio
async def test_users_service(uow: UOW):

    users = Users(
        accounts=Accounts(uow.session),
        emails=Emails(uow.session),
        phones=Phones(uow.session),
        credentials=Credentials(uow.session)        
    )

    async with uow:
        user = await users.create(name='test')
        user.events.append(Event(name='test', payload='test'))
        assert user.id is not None

    async with uow:
        user = await users.read(name='test')
        assert user.name == 'test'

    user = users.collection.pop()
    assert user.name == 'test'
    event = user.events.pop()
    assert event.name == 'test'

    with pytest.raises(Exception):
        user = users.collection.pop()