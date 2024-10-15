from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session, sessionmaker
from ..schemas.auth import User
from ..database import engine
import os

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
verification_token_expire_minutes = 30
password_reset_token_expire_minutes = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TokenData(BaseModel):
    email: Optional[str] = None

def create_token(data: dict, token_type: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if token_type == "access":
        expire_minutes = access_token_expire_minutes
    elif token_type == "verification":
        expire_minutes = verification_token_expire_minutes
    elif token_type == "password_reset":
        expire_minutes = password_reset_token_expire_minutes 
    else:
        raise ValueError("Invalid token type")
    
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=400, detail=f"Invalid {token_type} token")

def create_access_token(email: str) -> str:
    return create_token({"sub": email}, token_type="access")

def create_verification_token(email: str) -> str:
    return create_token({"sub": email}, token_type="verification")

def create_password_reset_token(email: str) -> str:
    return create_token({"sub: email"}, token_type="password_reset")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(role: str):
    def role_dependency(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Not enough privileges")
        return user
    return role_dependency

def create_reset_token(email: str) -> str:
    return create_token({"sub": email}, token_type="password_reset")

def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user
  