from typing import Annotated

from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.users.auth import exceptions
from src.users.auth.settings import Settings
from src.users.auth.adapters.accounts import Accounts
from src.users.auth.models.tokens import Token
from src.users.auth.models.credentials import Credential

class Auth:
    def __init__(self, settings: Settings):
        self.accounts = Accounts(settings)
        self.router = APIRouter(prefix=settings.auth_api_prefix)
        self.router.add_api_route('/login', self.login, methods=['POST'], response_model=Token)
        self.router.add_api_route('/register', self.register, methods=['POST'])
        self.bearer = OAuth2PasswordBearer(tokenUrl=f'{settings.auth_api_prefix}/login')

    def mount(self, api: FastAPI):
        api.include_router(self.router)

    async def login(self, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        try:
            async with self.accounts:
                account = await self.accounts.read(username=form.username)
                await account.authenticate(secret=form.password)
                return account.access_token()

        except exceptions.AccountNotFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Account with username not found'
            )
        
        except exceptions.InvalidCredentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid credentials'
            )
        
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            )
    

    async def register(self, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
        try:
            async with self.accounts:
                account = await self.accounts.create()
                account.credential = Credential(username=form.username, password=form.password)
                await account.save()
                
        except exceptions.AccountAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Account with username already exists'
            )
        
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(error)
            )