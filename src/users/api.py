import socket
from sqlalchemy import URL
from fastapi import FastAPI, Request
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from src.users.auth.endpoints import Auth
from src.users.auth.settings import Settings

database_url = URL.create(
        drivername = 'postgresql+asyncpg',
        username = 'postgres',
        password = 'postgres',
        host = socket.gethostbyname('postgres'),
        port = 5432,
        database = 'postgres'
    )

api = FastAPI(root_path="/api")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

auth = Auth(settings=Settings(database_uri=database_url, testing_mode=True))
auth.mount(api)

@api.get('/')
async def hello(bearer: str = Depends(auth.bearer)):
    return {'message': 'Hello, World!'}