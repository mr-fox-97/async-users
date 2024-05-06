from uuid import UUID, uuid4
from dataclasses import dataclass

from src.users.ports.accounts import Accounts
from src.users.ports.emails import Emails
from src.users.ports.phones import Phones
from src.users.ports.credentials import Credentials
from src.users.aggregate import User

@dataclass
class Repository:
    accounts: Accounts
    emails: Emails
    phones: Phones
    credentials: Credentials

    async def add(self, user: User):
        account = await self.accounts.create(username=user.name, userid=user.id)
        user.account = account
    
    async def get_by_name(self, name: str) -> User:
        account = await self.accounts.read(name)
        if account is None:
            return None
        user = User(account.username, account.user_id)
        user.account = account
        user.has_password = await self.credentials.check(account)
        return user