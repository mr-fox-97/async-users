from src.users.repository import Users as Repository
from src.users.adapters.accounts import Accounts
from src.users.adapters.credentials import Credentials
from src.users.adapters.emails import Emails
from src.users.adapters.phones import Phones
from src.services import Application, Service

class Users(Service, Repository):
    def __init__(self, bind: Application):
        super().__init__(bind)
        self.accounts = Accounts(self.session)
        self.emails = Emails(self.session)
        self.phones = Phones(self.session)
        self.credentials = Credentials(self.session)

        self.handlers['verify-password'] = lambda command: self.credentials.verify(command.issuer, command.payload)
        self.handlers['add-password'] = lambda command: self.credentials.add(command.issuer, command.payload)
        self.handlers['update-password'] = lambda command: self.credentials.update(command.issuer, command.payload)
        self.handlers['remove-password'] = lambda command: self.credentials.remove(command.issuer)