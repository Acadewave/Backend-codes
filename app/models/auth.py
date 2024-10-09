from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from typing import ClassVar

load_dotenv()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    role: str

class UserRoleResponse(BaseModel):
    user_id: int
    role: str

    class Config:
        from_attributes = True


class OAuthAccountResponse(BaseModel):
    provider: str
    provider_account_id: str
    access_token: str
    refresh_token: Optional[str]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class Settings(BaseSettings):
    MAIL_USERNAME: str 
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    TEMPLATE_FOLDER: str = "./app/templates"

    class MailConfig:
        env_file = ".env"

settings = Settings()



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
        from_attributes = True

        
