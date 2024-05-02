from uuid import UUID
from dataclasses import dataclass
from typing import List

from src.users.auth.models import Account, Email, Phone, Credential, Security
from src.users.domain import Aggregate, Command

class User(Aggregate):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account
        self.emails: List[Email] = []
        self.phones: List[Phone] = []
        self.has_password: bool = False

    @property
    def id(self) -> UUID:
        return self.account.user_id
    
    @property
    def name(self) -> str:
        return self.account.username
    
    @name.setter
    def name(self, value):
        task = Command('update-username', payload=Account(id=self.account.id, username=value), issuer=self.account)
        self.tasks.append(task)
    
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
        else:
            if value is not None:
                task = Command('create-password', payload=Credential(password=value), issuer=self.account)
            self.has_password = True
        self.tasks.append(task)