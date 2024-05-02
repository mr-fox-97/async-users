import pytest
import socket

from src.users.settings import URL, Settings
from src.users.settings import SQLAlchemySettings, FastAPISettings

@pytest.fixture(scope='session')
def url() -> URL:
    return URL.create(
        drivername = 'postgresql+asyncpg',
        username = 'postgres',
        password = 'postgres',
        host = socket.gethostbyname('postgres'),
        port = 5432,
        database = 'postgres'
    )

@pytest.fixture(scope='session')
def settings(url: URL) -> Settings:
    return Settings(
        testing_mode=True,
        
        orm=SQLAlchemySettings(
            uri=url,
            engine_echo=True,
            session_autoflush=False,
            session_autocommit=False,
            session_expire_on_commit=False
        ),

        api=FastAPISettings(
            auth_prefix='/auth',
        )
    )