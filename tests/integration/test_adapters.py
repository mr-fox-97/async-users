import pytest

from src.adapters import UnitOfWork as UOW

@pytest.mark.asyncio
async def test_uow(uow: UOW):
    async with uow:
        assert uow.session.is_active