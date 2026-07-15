from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    class config:
        from_attributes = True
        