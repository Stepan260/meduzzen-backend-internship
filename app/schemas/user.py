from datetime import datetime
from typing import Optional, List

import bcrypt
from pydantic import BaseModel, EmailStr, validator, UUID4


class UserBase(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]


class UserCreate(UserBase):
    password: str

    @validator('password')
    def hash_password(cls, v):
        return bcrypt.hashpw(v.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserDetail(UserBase):
    uuid: UUID4
    created_at: datetime = None
    updated_at: datetime = None


class UserListItem(BaseModel):
    uuid: str
    username: str


class UserListResponse(BaseModel):
    users: List[UserListItem]


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(UserCreate):
    pass
