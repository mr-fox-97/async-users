from uuid import UUID
from typing import Union
from datetime import datetime, timedelta
from typing import Annotated, Literal

from pydantic import BaseModel
from pydantic import SecretStr, EmailStr
from pydantic import ConfigDict
from pydantic import Field, field_serializer, field_validator
from passlib.context import CryptContext

class Account(BaseModel):
    id: int
    user_id: UUID
    username: str

def reveal(secret: Union[str, SecretStr]) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret

class Security:
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def is_hashed(cls, password : Union[str, SecretStr]) -> bool:
        if not cls.context.identify(reveal(password)):
            return False
        return True

    @classmethod
    def hash(cls, password : Union[str, SecretStr]) -> SecretStr:
        return SecretStr(cls.context.hash(reveal(password)))
    
    @classmethod
    def verify(cls, password : Union[str, SecretStr], hash : Union[str, SecretStr]) -> bool:
        if not password or not hash:
            return False
        try:
            return cls.context.verify(reveal(password), reveal(hash))
        except:
            return False

class Credential(BaseModel):
    password: SecretStr


class Email(BaseModel):
    id: int = None
    address: EmailStr 
    is_verified: bool = False
    is_primary: bool = False

class Phone(BaseModel):
    id: int = None
    number: str
    is_verified: bool = False
    is_primary: bool = False

class Token(BaseModel):
    model_config = ConfigDict(frozen=True)

    access_token: SecretStr
    token_type: Literal['bearer'] = 'bearer'

    @field_serializer('access_token')
    def reveal(self, access_token : SecretStr) -> str:
        return access_token.get_secret_value()

class Claim(BaseModel):
    model_config = ConfigDict(frozen=True)
    sub: Annotated[Union[str, UUID], Field(...)]
    exp: Annotated[Union[int, timedelta], Field(...)]
    iat: Annotated[Union[int, datetime], Field(default=int(datetime.now().timestamp()))]
    
    @field_validator('sub', mode='before')
    @classmethod
    def to_string(cls, raw : Union[str,UUID]) -> str:
        if isinstance(raw, UUID):
            return str(raw)
        return raw
    
    @field_validator('exp', mode='before')
    @classmethod
    def exp_to_unix(cls, raw : Union[int, timedelta]) -> int:
        if isinstance(raw, datetime):
            return int(raw.timestamp())
        if isinstance(raw, timedelta):
            return int((datetime.now() + raw).timestamp())
        return raw

#NOTE: The following descriptions are used to document the Claim model https://datatracker.ietf.org/doc/html/rfc7519
    # We should implement them all in the Claim model
SUB_DESCRIPTION = "Defines the entity associated with the claim."
EXP_DESCRIPTION = "Specifies the expiration time of the token, indicating when it becomes invalid."
IAT_DESCRIPTION = "Denotes the exact moment when the JWT was generated."
NBF_DESCRIPTION = "Indicates the earliest time at which the token becomes valid."
ISS_DESCRIPTION = "Identifies the authority or entity responsible for issuing the JWT."
AUD_DESCRIPTION = "Designates the specific recipient or audience intended to receive the JWT."