from typing import Union
from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import URL

DATABASE_URI_DESCRIPTION = 'URL of the database to connect to'
DATABASE_ENGINE_ECHO_DESCRIPTION = 'Enable SQLAlchemy logging (True to log all SQL statements)'
DATABASE_SESSION_AUTOFLUSH_DESCRIPTION = 'Enable autoflush (True to flush changes to the database before queries)'
DATABASE_SESSION_AUTOCOMMIT_DESCRIPTION = 'Enable autocommit mode (True to commit each SQL statement automatically)'
DATABASE_SESSION_EXPIRE_ON_COMMIT_DESCRIPTION = 'Enable expire_on_commit (True to expire all objects attached to the session after commit)'
TESTING_MODE_DESCRIPTION = 'Rollback transactions when exiting context manager (True to rollback, False to commit)'

class Settings(BaseSettings):
    testing_mode: bool = Field(default=False, description=TESTING_MODE_DESCRIPTION)
    database_uri: Union[str, URL] = Field(description=DATABASE_URI_DESCRIPTION)
    database_engine_echo: bool = Field(default=True, description=DATABASE_ENGINE_ECHO_DESCRIPTION)
    database_session_autoflush: bool = Field(default=False, description=DATABASE_SESSION_AUTOFLUSH_DESCRIPTION)
    database_session_autocommit: bool = Field(default=False, description=DATABASE_SESSION_AUTOCOMMIT_DESCRIPTION)
    database_session_expire_on_commit: bool = Field(default=True, description=DATABASE_SESSION_EXPIRE_ON_COMMIT_DESCRIPTION)
    auth_api_prefix: str = Field(default='/auth', description='Prefix for the authentication API')