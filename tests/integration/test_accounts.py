import pytest
from sqlalchemy import URL

from src.users.auth import handlers
from src.users.settings import Settings
from src.users.auth.repository.accounts import Accounts
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
    accounts = Accounts(settings)
    return accounts


@pytest.mark.asyncio
async def test_accounts(accounts: Accounts):
    async with accounts:
        account = await accounts.create()
        account.credential = Credential(username='test', password='test')
        await account.save()

        account = await accounts.read(username='test')
        assert account.credential.username == 'test'
        assert account.credential.verify(password='test')    

        account.credential = Credential(username='test', password='updated')
        await account.save()

        assert account.credential.verify(password='updated')

        account = await accounts.read(username='test')
        assert account.credential.verify(password='updated')

        with pytest.raises(Exception):
            await account.authenticate(password='invalid')