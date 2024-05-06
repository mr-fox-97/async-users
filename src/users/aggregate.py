from uuid import UUID
from typing import List
from src.domain import Aggregate, Event, Command
from src.users.models import Account, Email, Phone, Credential

class User(Aggregate):
    def __init__(self, id: UUID, name: str):
        self.account: Account = None
        self.id = id
        self.name = name
        self.has_password = False

    @property
    def root(self):
        return self.account
    
    @property
    def password(self) -> str:
        return "********" if self.has_password else None
    
    @password.setter
    def password(self, value):
        if self.has_password:
            if value is not None:
                event = Event('password-updated', payload=Credential(password=value), publisher=self)
            else:
                event = Event('password-removed',  payload=Credential(password=value), publisher=self)
                self.has_password = False
        else:
            if value is not None:
                event = Event('password-created', payload=Credential(password=value), publisher=self)
            self.has_password = True
        self.publish(event)
    
    async def verify(self, password: str) -> bool:
        if not self.has_password:
            return False
        command = Command(name='verify-password', payload=Credential(password=password), issuer=self)
        verified = await self.execute(command)
        return verified