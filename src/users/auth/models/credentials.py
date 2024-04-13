from uuid import UUID, uuid4
from pydantic import SecretStr
from pydantic import Field, field_validator
from pydantic import BaseModel, ConfigDict
from src.users.auth.models.security import Security

class Credential(BaseModel):
    account_id: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=50)
    password: SecretStr = Field(...)

    def verify(self, secret: SecretStr) -> bool:
        return Security.verify(secret, self.password)
    
    @field_validator('password', mode='after')
    @classmethod
    def hash_password(cls, value: SecretStr) -> SecretStr:
        return value if Security.is_hashed(value) else Security.hash(value)
    
    model_config = ConfigDict(validate_assignment=True)