from typing import Annotated

from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.users.auth import exceptions
from src.users.auth.settings import Settings
from src.users.auth.adapters import Accounts
from src.users.auth.models.tokens import Token

class Auth:
    def __init__(self, settings: Settings):
        self.accounts = Accounts(settings)
        self.router = APIRouter(prefix=settings.auth_api_prefix)
        self.router.add_api_route('/login', self.login, methods=['POST'], response_model=Token)
        self.router.add_api_route('/register', self.register, methods=['POST'], response_model=Token)
        self.bearer = OAuth2PasswordBearer(tokenUrl=f'{settings.auth_api_prefix}/login')

    def mount(self, api: FastAPI):
        api.include_router(self.router)

    async def login(self, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        async with self.accounts:
            try:
                account = await self.accounts.read(username=form.username)
                return account.authenticate(secret=form.password)

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
    

    async def register(self, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        async with self.accounts:
            try:
                account = await self.accounts.create(username=form.username, password=form.password)
                return account.authenticate(secret=form.password)

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