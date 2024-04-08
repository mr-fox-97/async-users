import pytest
import socket
from typing import Generator
from typing import Any

from sqlalchemy import URL

@pytest.fixture(scope='session')
def url() -> Generator[URL, Any, None]:
    yield URL.create(
        drivername = 'postgresql+asyncpg',
        username = 'postgres',
        password = 'postgres',
        host = socket.gethostbyname('postgres'),
        port = 5432,
        database = 'postgres'
    )