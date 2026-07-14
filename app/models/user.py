import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from app.core.database import Base

from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"
    
    id : Mapped[uuid.UUID] = mapped_column(primary_key = True, default = uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable = False, index = True, unique = True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True, nullable = False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )