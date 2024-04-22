from typing import Any
from dataclasses import dataclass

from src.users.ports import Root
from src.users.auth.models.accounts import Account

@dataclass
class Attributes:
    identity: Any
    handlers: dict
    events: list

class User(Root):
    def __init__(self, __attributes: Attributes):
        super().__init__(__attributes.identity, __attributes.handlers, __attributes.events)