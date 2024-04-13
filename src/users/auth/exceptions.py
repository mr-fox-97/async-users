class AccountAlreadyExists(Exception):
    def __init__(self, message="Account already exists", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class AccountNotFound(Exception):
    def __init__(self, message="Account not found", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class InvalidCredentials(Exception):
    def __init__(self, message="Incorrect password", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class TokenError(Exception):
    def __init__(self, message="Invalid token", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class TokenExpired(Exception):
    def __init__(self, message="Expired token", *args, **kwargs):
        super().__init__(message, *args, **kwargs)