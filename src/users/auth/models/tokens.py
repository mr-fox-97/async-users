import secrets
from typing import Annotated
from datetime import datetime, timedelta
from uuid import UUID
from typing import Literal
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import SecretStr
from pydantic import Field
from pydantic import field_validator
from pydantic import field_serializer
from jose import jwt
from jose import JWTError
from jose import ExpiredSignatureError
from pydantic import SecretStr

from src.users.auth import exceptions

class Token(BaseModel):
    model_config = ConfigDict(frozen=True)

    access_token: SecretStr
    token_type: Literal['bearer'] = 'bearer'

    @field_serializer('access_token')
    def reveal(self, access_token : SecretStr) -> str:
        return access_token.get_secret_value()

#NOTE: The following descriptions are used to document the Claim model https://datatracker.ietf.org/doc/html/rfc7519
    # We should implement them all in the Claim model
SUB_DESCRIPTION = "Defines the entity associated with the claim."
EXP_DESCRIPTION = "Specifies the expiration time of the token, indicating when it becomes invalid."
IAT_DESCRIPTION = "Denotes the exact moment when the JWT was generated."
NBF_DESCRIPTION = "Indicates the earliest time at which the token becomes valid."
ISS_DESCRIPTION = "Identifies the authority or entity responsible for issuing the JWT."
AUD_DESCRIPTION = "Designates the specific recipient or audience intended to receive the JWT."

class Claim(BaseModel):
    model_config = ConfigDict(frozen=True)
    sub: Annotated[Union[str, UUID], Field(..., description=SUB_DESCRIPTION)]
    exp: Annotated[Union[int, timedelta], Field(..., description=EXP_DESCRIPTION)]
    iat: Annotated[Union[int, datetime], Field(default=int(datetime.now().timestamp()), description=IAT_DESCRIPTION)]
    
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


class Tokenizer:
    secret : SecretStr = SecretStr(secrets.token_hex(16))

    @classmethod
    def encode(cls, claim : Claim, algorithm : str = 'HS256') -> Token:
        encoded_token = jwt.encode(
            claim.model_dump() , 
            cls.secret.get_secret_value(), 
            algorithm = algorithm
        )
        return Token(access_token = encoded_token, token_type = 'bearer')

    @classmethod
    def decode(cls, token : Token) -> Claim:
        try:
            decoded_token = jwt.decode(
                token.access_token.get_secret_value(), 
                cls.secret.get_secret_value(), 
                algorithms = ['HS256']
            )
            return Claim(**decoded_token)
        
        except ExpiredSignatureError:
            raise exceptions.TokenExpired
        
        except JWTError:
            raise exceptions.TokenError