import pytest
import asyncio

from src.users.adapters import ObjectRelationalMapper as ORM
from src.users.adapters import DataAccessObject as DAO
from src.users.adapters import UnitOfWork as UOW

from src.users.auth.adapters.accounts import Accounts
from src.users.auth.adapters.credentials import Credentials

from src.users.auth.models import Credential
from src.users.auth.models import Email, Phone

@pytest.fixture(scope='function')
async def accounts(sessionmaker):
    return Accounts(sessionmaker)

@pytest.mark.asyncio
async def test_accounts(accounts: Accounts):

    async with accounts:
        account = await accounts.create('test')
        id = account.id
        userid = account.user_id

    async with accounts:
        account = await accounts.read('test')
        assert account.id == id
        assert account.user_id == userid

    async with accounts:
        account = await accounts.get(userid)
        assert account.id == id

    async with accounts:
        await accounts.delete(account)
        account = await accounts.get(userid)
        assert account is None


@pytest.mark.asyncio
async def test_credentials(accounts: Accounts):

    async with accounts:
        account = await accounts.create('test')
        assert not await accounts.credentials.check(account)
        await accounts.credentials.add(account, Credential(password='test'))

    async with accounts:
        assert await accounts.credentials.check(account)
        assert await accounts.credentials.verify(account, Credential(password='test'))
        assert not await accounts.credentials.verify(account, Credential(password='wrong'))

    async with accounts:
        await accounts.credentials.update(account, Credential(password='new'))

    async with accounts:
        assert await accounts.credentials.verify(account, Credential(password='new'))
        assert not await accounts.credentials.verify(account, Credential(password='test'))


@pytest.mark.asyncio
async def test_emails(accounts: Accounts):
    async with accounts:
        account = await accounts.create(username='test')
        await accounts.emails.add(account, Email(address="test@test.com"))
        await accounts.emails.add(account, Email(address="test2@test.com"))
        await accounts.emails.add(account, Email(address="test3@test.com"))

    async with accounts:
        emails = await accounts.emails.get(account)
        assert len(emails) == 3
        second_email = emails[1]
        await accounts.emails.remove(second_email)

    async with accounts:
        emails = await accounts.emails.get(account)
        assert len(emails) == 2
        assert emails[0].address == "test@test.com"
        assert emails[1].address == "test3@test.com"

    async with accounts:
        account = await accounts.emails.find("test3@test.com")
        assert account.username == 'test'

    async with accounts:
        await accounts.emails.clear(account)
        emails = await accounts.emails.get(account)
        assert len(emails) == 0


@pytest.mark.asyncio
async def test_phones(accounts: Accounts):
    async with accounts:
        account = await accounts.create(username='test')
        await accounts.phones.add(account, Phone(number="123456789"))
        await accounts.phones.add(account, Phone(number="223456789"))
        await accounts.phones.add(account, Phone(number="323456789"))

    async with accounts:
        phones = await accounts.phones.get(account)
        assert len(phones) == 3
        second_phone = phones[1]
        await accounts.phones.remove(second_phone)

    async with accounts:
        phones = await accounts.phones.get(account)
        assert len(phones) == 2
        assert phones[0].number == "123456789"
        assert phones[1].number == "323456789"

    async with accounts:
        account = await accounts.phones.find("323456789")
        assert account.username == 'test'

    async with accounts:
        await accounts.phones.clear(account)
        phones = await accounts.phones.get(account)
        assert len(phones) == 0