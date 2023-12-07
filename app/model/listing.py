from pydantic import BaseModel
from typing import Optional

class Property(BaseModel):
    property_id: Optional[int] = None
    title: Optional[str] = None
    rating: Optional[float] = None
    summary: Optional[str] = None
    price: Optional[int] = None
    location: Optional[str] = None
    booking_history: Optional[list] = None