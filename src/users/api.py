from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI(root_path="/api")
api.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
