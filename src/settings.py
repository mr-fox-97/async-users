from typing import Union, Annotated
from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import URL

DATABASE_URI_DESCRIPTION = 'URL of the database to connect to'
DATABASE_ENGINE_ECHO_DESCRIPTION = 'Enable SQLAlchemy logging (True to log all SQL statements)'
DATABASE_SESSION_AUTOFLUSH_DESCRIPTION = 'Enable autoflush (True to flush changes to the database before queries)'
DATABASE_SESSION_AUTOCOMMIT_DESCRIPTION = 'Enable autocommit mode (True to commit each SQL statement automatically)'
DATABASE_SESSION_EXPIRE_ON_COMMIT_DESCRIPTION = 'Enable expire_on_commit (True to expire all objects attached to the session after commit)'
TESTING_MODE_DESCRIPTION = 'Rollback transactions when exiting context manager (True to rollback, False to commit)'

class SQLAlchemySettings(BaseSettings):
    uri: Annotated[Union[str, URL], Field(description=DATABASE_URI_DESCRIPTION)]
    engine_echo: Annotated[bool, Field(default=True, description=DATABASE_ENGINE_ECHO_DESCRIPTION)]
    session_autoflush: Annotated[bool, Field(default=False, description=DATABASE_SESSION_AUTOFLUSH_DESCRIPTION)]
    session_autocommit: Annotated[bool, Field(default=False, description=DATABASE_SESSION_AUTOCOMMIT_DESCRIPTION)]
    session_expire_on_commit: Annotated[bool, Field(default=True, description=DATABASE_SESSION_EXPIRE_ON_COMMIT_DESCRIPTION)]

class FastAPISettings(BaseSettings):
    users_prefix: str
    auth_prefix: str

class Settings(BaseSettings):
    orm: SQLAlchemySettings