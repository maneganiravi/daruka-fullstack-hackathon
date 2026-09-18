from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = None
    role: Optional[str] = "user"


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Properties returned via API (exclude hashed_password)
class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# Token payload
class TokenPayload(BaseModel):
    sub: Optional[str] = None
