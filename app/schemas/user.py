from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str]


class UserDetail(UserBase):
    uuid: str
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    users: List[UserDetail]


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(UserCreate):
    pass
