from src.users.ports import Event
from src.users.auth.models.credentials import Credential

class CredentialAdded(Event):
    type: str = 'credential-added'
    payload: Credential

class CredentialUpdated(Event):
    type: str = 'credential-updated'
    payload: Credential

class CredentialRemoved(Event):
    type: str = 'credential-removed'
    payload: Credential