from src.users.settings import URL, Settings
from src.users.adapters import ObjectRelationalMapper as ORM

class Application:
    def __init__(self, settings: Settings):
        self.testing_mode = settings.testing_mode
        self.orm = ORM(settings)