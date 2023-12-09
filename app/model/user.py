from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    password: Optional[str] = None
    trips: Optional[object] = None
    userType: Optional[str] = None 