from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api import api

templates = Jinja2Templates(directory="src/templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/sign-in", response_class=HTMLResponse)
async def sign_in_page(request: Request):
    return templates.TemplateResponse(
        request=request, name='sign-in.html'
    )

@app.get("/sign-up", response_class=HTMLResponse)
async def sign_up_page(request: Request):
    return templates.TemplateResponse(
        request=request, name='sign-up.html'
    )