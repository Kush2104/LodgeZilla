# app/main.py
from fastapi import FastAPI
from fastapi import APIRouter
from . import app_router

app = FastAPI()

app.include_router(app_router)