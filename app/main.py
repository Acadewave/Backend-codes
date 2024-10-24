from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware 
from app.routers.auth import router
from app.schemas.auth import Base
from app.database import engine

app = FastAPI(
    title="Acadewave",
    description="Learning Management System API",
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SessionMiddleware, secret_key="supersecretkey")  
Base.metadata.create_all(bind=engine)


app.include_router(router)
