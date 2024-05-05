from uuid import UUID
from typing import Union
from pydantic import BaseModel
from pydantic import SecretStr, EmailStr
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
    password: Union[SecretStr, None] 

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