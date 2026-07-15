from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

from app.api.v1.auth import router as auth_router

app = FastAPI(title = "DocuSense API", version = "0.1.0")
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the DocuSense API"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Execute a shallow query against the live database
        result = await db.execute(text("SELECT 1"))
        op = result.scalar()
        return {"status": "healthy", "database": "connected", "output": op}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )