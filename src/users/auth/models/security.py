from typing import Union

from pydantic import SecretStr
from passlib.context import CryptContext

def reveal(secret : Union[str, SecretStr]) -> str:
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
            return cls.context.verify(secret = reveal(password), hash = reveal(hash))
        except:
            return False