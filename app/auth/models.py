import uuid
from fastapi_users import schemas
from pydantic import EmailStr
from sqlalchemy import Boolean, Column, Integer, String, Enum
from app.auth.base import Base
from enum import Enum as PyEnum
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

class UserRoleEnum(PyEnum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(SQLAlchemyBaseUserTable, Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRoleEnum), nullable=False)

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    role: UserRoleEnum

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRoleEnum
