import functools
from abc import ABC
from typing import Protocol
from typing import Dict
from typing import Callable
from typing import Any
from typing import TypeVar, Generic

from src.services import ObjectRelationalMapper as ORM

class Session(Protocol):
    
    async def begin(self):
        pass

    async def rollback(self):
        pass

    async def close(self):
        pass

    async def commit(self):
        pass


class DataAccessObject:
    def __init__(self, session: Session):
        self.session = session

    async def begin(self):
        await self.session.begin()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()


class UnitOfWork:
    def __init__(self, orm: ORM):
        self.engine = orm.engine
        self.session = orm.sessionmaker(bind=self.engine)
        
    async def begin(self):
        await self.session.begin()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def __aenter__(self):
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()