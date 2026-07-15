from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_password, hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix = "/v1/auth",
    tags = ["auth"]
)

@router.post("/register", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    

    if existing_user and existing_user.email == user.email: 
        raise HTTPException(
            status_code= 400,
            detail= "Email already registered"
        )
        
    new_user = User(
        email = user.email,
        hashed_password = hash_password(user.password)
    )
    
    db.add(new_user)
    
    await db.commit()
    
    await db.refresh(new_user)
    return new_user

