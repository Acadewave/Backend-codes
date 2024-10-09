from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException

import os
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
verification_token_expire_minutes = 30  

class TokenData(BaseModel):
    email: Optional[str] = None

def create_token(data: dict, token_type: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if token_type == "access":
        expire_minutes = access_token_expire_minutes
    elif token_type == "verification":
        expire_minutes = verification_token_expire_minutes
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
