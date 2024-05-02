from src.users.adapters import ObjectRelationalMapper as ORM
from src.users.adapters import UnitOfWork as UOW

async def test_orm(orm: ORM):
    engine = orm.engine
    connection = await engine.connect()
    transaction = await connection.begin()
    assert transaction.is_active
    await transaction.rollback()
    await connection.close()
    assert not transaction.is_active

async def test_uow(uow: UOW):
    async with uow:
        assert uow.transaction.is_active