from dataclasses import dataclass

class Event:
    pass

@dataclass
class Authenticated(Event):
    message: str