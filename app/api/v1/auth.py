from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.security import verify_password, hash_password, create_access_token
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

@router.post("/login")
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = create_access_token(data={"sub": str(user.id)})
    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer"
    # }
    return JSONResponse(
        status_code= status.HTTP_202_ACCEPTED,
        content = {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
