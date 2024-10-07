from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    role: str

class UserRoleResponse(BaseModel):
    user_id: int
    role: str

    class Config:
        orm_mode = True


class OAuthAccountResponse(BaseModel):
    provider: str
    provider_account_id: str
    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]

    class Config:
        orm_mode = True


class PasswordResetTokenCreate(BaseModel):
    email: EmailStr  

class PasswordResetTokenVerify(BaseModel):
    token: str 

class PasswordResetTokenResponse(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime

    class Config:
        orm_mode = True
