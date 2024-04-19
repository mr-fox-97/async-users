from uuid import UUID
from datetime import timedelta
from typing import Protocol
from typing import Deque
from typing import Dict, List, Callable
from collections import deque
from pydantic import SecretStr

from src.users.auth import exceptions
from src.users.auth.models import events
from src.users.auth.models.events import Event
from src.users.auth.models.credentials import Credential
from src.users.auth.models.tokens import Token, Claim, Tokenizer

class Credential(Protocol):
    username: str
    def verify(self, secret: SecretStr) -> bool:
        ...

async def publish_online_status(event: events.Authenticated):
    print(f"User is online")

class Account:
    def __init__(self, identity):
        self.identity = identity
        self.credential: Credential = None
        self.access_token: Token = None
        self.events: Deque[Event] = deque()
        self.handlers: Dict[Event, List[Callable]] = {
            events.Authenticated: [ lambda event: publish_online_status(event) ]
        }

    @property
    def id(self):
        return self.identity
    
    @property
    def username(self):
        if self.credential:
            return self.credential.username
        return None
    
    async def handle(self, event: Event):
        self.events.append(event)
        while self.events:
            event = self.events.popleft()
            for handler in self.handlers[type(event)]:
                await handler(event)
        
    async def authenticate(self, secret: SecretStr, session_duration: timedelta = timedelta(days=1)):
        if not self.credential.verify(secret):
            raise exceptions.InvalidCredentials("Invalid credentials")
        self.access_token = Tokenizer.encode(claim=Claim(sub=self.id, exp=session_duration))
        await self.handle(events.Authenticated("Account authenticated"))

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)