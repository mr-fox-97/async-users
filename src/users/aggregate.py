from uuid import UUID
from src.domain import Entity, Root, Command
from src.users.models import Account, Credential

class User(Entity, Root):
    def __init__(self, account: Account):
        self.account = account
        self.has_password = False
    
    @property
    def id(self) -> UUID:
        return self.account.user_id
    
    @property
    def name(self) -> str:
        return self.account.username
    
    @property
    def password(self) -> str:
        return "********" if self.has_password else None
    
    @password.setter
    def password(self, value):
        if self.has_password:
            if value is not None:
                task = Command('update-password', payload=Credential(password=value), issuer=self.account)
            else:
                task = Command('remove-password',  payload=Credential(password=value), issuer=self.account)
                self.has_password = False
        else:
            if value is not None:
                task = Command('add-password', payload=Credential(password=value), issuer=self.account)
            self.has_password = True
        self.tasks.append(task)
    
    async def verify(self, password: str) -> bool:
        command = Command(name='verify-password', payload=Credential(password=password), issuer=self.account)
        verified = await self.execute(command)
        return verified