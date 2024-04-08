import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_connection(session: AsyncSession):
    assert session.is_active