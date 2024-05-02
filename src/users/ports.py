from typing import Protocol

class UnitOfWork(Protocol):

    async def begin(self):
        ...

    async def close(self):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        ...