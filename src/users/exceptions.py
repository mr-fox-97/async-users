class AccountAlreadyExists(Exception):
    def __init__(self, message="Account already exists", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class AccountNotFound(Exception):
    def __init__(self, message="Account not found", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class InvalidCredentials(Exception):
    def __init__(self, message="Invalid credentials", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class InvalidPassword(Exception):
    def __init__(self, message="Invalid password", *args, **kwargs):
        super().__init__(message, *args, **kwargs)