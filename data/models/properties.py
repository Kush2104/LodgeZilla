from pydantic import BaseModel

class Property(BaseModel):
    title: str
    description: str
    price_per_night: float
    location: str
