from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..schemas.auth import User
from ..models.auth import UserCreate, UserResponse, PasswordResetRequest, PasswordResetUpdate
from ..database import get_db
from ..utils.jwt import create_access_token, create_verification_token, verify_token, role_required, create_reset_token, get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from ..models.auth import UserLogin, settings
from fastapi.security import OAuth2PasswordBearer
from ..utils.email import send_verification_email, send_password_reset_email
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth



config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=config('GOOGLE_REDIRECT_URI'),  
    client_kwargs={'scope': 'openid email profile'}
)

base_url = "https://backend-codes-l8uf.onrender.com"

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_FOLDER)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def get_user_by_email_or_username(db: Session, login_input: str):
    return db.query(User).filter(
        (User.email == login_input) | (User.username == login_input)
    ).first()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, request: Request, db: Session = Depends(get_db), ):
    existing_user = db.query(User).filter(
        (User .email == user.email) | (User .username == user.username)
    ).first()

    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    token = create_verification_token(new_user.email)
    await send_verification_email(new_user.email, token, request)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.get("/auth/login-google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')  # The URL to redirect after successful login
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    email = user_info.get('email')
    name = user_info.get('name')

    user = db.query(User).filter(User.email == email).first()

    if not user:
        role = "student"
        user = User(email=email, username=name)  
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.email)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email_or_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/send-verification-email", response_class=HTMLResponse)
async def send_verification_email(email:str, token: str, request: Request):
    verification_link = f"{base_url}/verify-email?token={token}"
    return templates.TemplateResponse("email/verification_email.html", {"request": request, "verification_link": verification_link})


def verify_verification_token(token: str):
    try:
        token_data = verify_token(token, token_type="verification")
        return token_data.email
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = verify_verification_token(token)
        
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        if user.is_active:
            raise HTTPException(status_code=400, detail="Email already verified")
        user.is_active = True       
        db.commit()
        return {"msg": "Email verified successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/password-reset-request")
async def password_reset_request(data: PasswordResetRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == data.login) | (User.username == data.login)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    base_url = "https://backend-codes-l8uf.onrender.com"
    

    reset_link = f"{base_url}/reset-password?token={create_reset_token}"

    await send_password_reset_email(user.email, reset_link, request)
    
    return {"message": "Password reset link sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordResetUpdate, db: Session = Depends(get_db)):
    token_data = verify_token(data.token, token_type="password_reset")    
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(data.new_password)
    

@router.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db), user: User = Depends(role_required("admin"))):
    return {"message": "Welcome to the admin dashboard!"}
