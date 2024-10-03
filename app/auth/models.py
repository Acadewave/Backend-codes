import uuid
from fastapi_users import schemas
from pydantic import EmailStr
from sqlalchemy import Boolean, Column, Integer, String, Enum
from app.auth.base import Base
from enum import Enum as PyEnum
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.dialects.postgresql import UUID

class UserRoleEnum(PyEnum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(SQLAlchemyBaseUserTable, Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRoleEnum), nullable=False)

class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    password: str

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    username: str
    password: str
    role: UserRoleEnum

class UserUpdate(schemas.BaseUserUpdate):
    role: UserRoleEnum
