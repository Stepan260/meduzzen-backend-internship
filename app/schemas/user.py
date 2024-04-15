from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str]


class UserDetail(UserBase):
    uuid: str
    created_at: datetime = None
    updated_at: datetime = None


class UserListResponse(BaseModel):
    users: List[UserDetail]


class UserListItem(BaseModel):
    uuid: str
    username: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(UserCreate):
    pass
