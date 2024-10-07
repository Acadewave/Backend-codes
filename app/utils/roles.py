from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.user import UserRole
from ..database import get_db
from ..utils.jwt import verify_token

def get_current_user_role(token: str, db: Session = Depends(get_db)):
    token_data = verify_token(token)
    user_role = db.query(UserRole).filter(UserRole.user_id == token_data.email).first()
    if not user_role:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return user_role.role


def role_required(required_role: str):
    def decorator(current_role: str = Depends(get_current_user_role)):
        if current_role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True
    return decorator
