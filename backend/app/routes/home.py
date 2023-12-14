from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_listings():
    return "This is the home"
