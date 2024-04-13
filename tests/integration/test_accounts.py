import pytest
from uuid import UUID
from sqlalchemy import URL, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.auth.settings import Settings
from src.users.auth.schemas import accounts as accounts_table
from src.users.auth.adapters import Accounts
from src.users.auth.models.accounts import Account
from src.users.auth.models.credentials import Credential, SecretStr

@pytest.fixture
def settings(url: URL) -> Settings:
    return Settings(
        database_uri = url,
        database_engine_echo = True,
        database_session_autoflush = False,
        database_session_autocommit = False,
        database_session_expire_on_commit = False,
        testing_mode = True
    )

@pytest.fixture
def accounts(settings: Settings) -> Accounts:
    return Accounts(settings)

@pytest.mark.asyncio
async def test_accounts_transactions(accounts: Accounts):
    '''
        This tests the transactional behavior of the Accounts unit of work class
        here we commit the insert operation but as we set up the testing mode, the 
        transaction is rolled back when exiting the context manager

    '''
    account = Account(identity=UUID('00000000-0000-0000-0000-000000000000'))

    async with accounts:
        await accounts.add(account)
        result = await accounts.session.execute(
            select(accounts_table).where(accounts_table.id == account.id)
        )
        account = result.scalars().first()
        assert account is not None
        await accounts.commit()


    account = Account(identity=UUID('00000000-0000-0000-0000-000000000000'))
    async with accounts:
        result = await accounts.session.execute(
            select(accounts_table).where(accounts_table.id == account.id)
        )
        account = result.scalars().first()
        assert account is None


@pytest.mark.asyncio
async def test_accounts(accounts: Accounts):
    async with accounts:
        account = await accounts.create(username='test', password='test')
        assert account.credential.username == 'test'
        assert account.credential.verify(secret='test')

        account = await accounts.read(username='test')
        assert account.credential.username == 'test'
        assert account.credential.verify(secret='test')