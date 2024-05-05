import pytest

from src.adapters import UnitOfWork as UOW
from src.users.models import Account, Credential, Email, Phone
from src.users.adapters.accounts import Accounts
from src.users.adapters.credentials import Credentials
from src.users.adapters.emails import Emails
from src.users.adapters.phones import Phones

@pytest.mark.asyncio
async def test_accounts(uow: UOW):
    accounts = Accounts(uow.session)

    async with accounts:
        account = await accounts.create(username='test')
        assert account.id is not None
        await accounts.commit()

    async with accounts:
        account = await accounts.read(username='test')
        assert account.username == 'test'
        account = Account(id=account.id, user_id=account.user_id, username='new')
        await accounts.update(account)
        await accounts.commit()

    async with accounts:
        account = await accounts.read(username='new')
        assert account.username == 'new'
        await accounts.delete(account)
        await accounts.commit()

    async with accounts:
        account = await accounts.read(username='new')
        assert account is None


@pytest.mark.asyncio
async def test_credentials(uow: UOW):
    credentials = Credentials(uow.session)
    accounts = Accounts(uow.session)

    async with accounts:
        account = await accounts.create(username='test')
        await accounts.commit()

    async with credentials:
        credential = Credential(password='password123')
        await credentials.add(account, credential)

    async with credentials:
        credential = Credential(password='password123')
        assert await credentials.verify(account, credential)

    async with credentials:
        credential = Credential(password='newpassword')
        await credentials.update(account, credential)

    async with credentials:
        credential = Credential(password='newpassword')
        assert await credentials.verify(account, credential)

    async with credentials:
        assert await credentials.check(account)

    async with credentials:
        await credentials.remove(account)

    async with credentials:
        assert not await credentials.check(account)


@pytest.mark.asyncio
async def test_emails(uow: UOW):
    emails = Emails(uow.session)
    accounts = Accounts(uow.session)

    async with accounts:
        account = await accounts.create(username='test')
        assert account.id is not None
        await accounts.commit()

    async with emails:
        email = Email(address='test@example.com', is_verified=True, is_primary=True)
        await emails.add(account, email)

    async with emails:
        emails_list = await emails.get(account)
        assert len(emails_list) == 1
        assert emails_list[0].address == 'test@example.com'

    async with emails:
        email = Email(address='new@example.com', is_verified=False, is_primary=False)
        await emails.add(account, email)

    async with emails:
        emails_list = await emails.get(account)
        assert len(emails_list) == 2

    async with emails:
        await emails.remove(email)

    async with emails:
        emails_list = await emails.get(account)
        assert len(emails_list) == 1

    async with emails:
        await emails.clear(account)

    async with emails:
        emails_list = await emails.get(account)
        assert len(emails_list) == 0

    async with emails:
        found_account = await emails.find('test@example.com')
        assert found_account is None

    async with emails:
        email = Email(address='test@example.com', is_verified=True, is_primary=True)
        await emails.add(account, email)

    async with emails:
        found_account = await emails.find('test@example.com')
        assert found_account.id == account.id


@pytest.mark.asyncio
async def test_phones(uow: UOW):
    phones = Phones(uow.session)
    accounts = Accounts(uow.session)

    async with accounts:
        account = await accounts.create(username='test')
        assert account.id is not None
        await accounts.commit()

    async with phones:
        phone = Phone(number='1234567890', is_verified=True, is_primary=True)
        await phones.add(account, phone)

    async with phones:
        phones_list = await phones.get(account)
        assert len(phones_list) == 1
        assert phones_list[0].number == '1234567890'

    async with phones:
        phone = Phone(number='0987654321', is_verified=False, is_primary=False)
        await phones.add(account, phone)

    async with phones:
        phones_list = await phones.get(account)
        assert len(phones_list) == 2

    async with phones:
        await phones.remove(phone)

    async with phones:
        phones_list = await phones.get(account)
        assert len(phones_list) == 1

    async with phones:
        await phones.clear(account)

    async with phones:
        phones_list = await phones.get(account)
        assert len(phones_list) == 0

    async with phones:
        found_account = await phones.find('1234567890')
        assert found_account is None

    async with phones:
        phone = Phone(number='1234567890', is_verified=True, is_primary=True)
        await phones.add(account, phone)

    async with phones:
        found_account = await phones.find('1234567890')
        assert found_account.id == account.id