from fastapi_users import FastAPIUsers, models
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.db.session import get_user_db
from app.auth.models import User, UserCreate, UserUpdate, UserRead
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from typing import List 
from app.db.session import get_db
from sqlalchemy import text 
import uuid
import os


SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_db,  
    [auth_backend],  
)


auth_router = APIRouter()


auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),  
    prefix="/auth/jwt", 
    tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),  
    prefix="/auth",
    tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)

def require_role(roles: List[str]):
    def role_checker(user: User = Depends(fastapi_users.get_current_active_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return role_checker

#Testing db
@auth_router.get("/test-connection")
def test_connection(db: Session = Depends(get_db)):
    try:
        # Test by running a simple query
        result = db.execute(text("SELECT 1")).fetchone()  # Use text() to declare the SQL expression
        return {
            "success": True,
            "message": "Successfully connected to the database",
            "result": result[0] if result else None  # Extract the first item from the result
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }