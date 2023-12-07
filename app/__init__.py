from fastapi import APIRouter
from .routes import listings
from .routes import home
from .routes import auth

app_router = APIRouter()
app_router.include_router(listings.router, prefix="/listings", tags=["listings"])
app_router.include_router(home.router, tags=["home_page"])
app_router.include_router(auth.router, prefix="/auth", tags=["token"])
