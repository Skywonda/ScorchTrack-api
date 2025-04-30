# In app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

from app.api.routes import auth, users, routines, progress, whatsapp
from app.config import settings
from app.core.scheduler import scheduler
from app.db.database import Base, engine, create_tables, drop_tables

create_tables()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    The ScorchTrack API powers an innovative accountability system that combines 
    daily routine tracking with personalized feedback through WhatsApp.
    
    The unique twist is incorporating AI-powered "roasting" for underperforming team members, 
    adding a fun, competitive element to accountability challenges.
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "ScorchTrack Support",
        "email": "support@scorchtrack.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_STR}/auth", 
    tags=["Authentication"]
)
app.include_router(
    users.router, 
    prefix=f"{settings.API_V1_STR}/users", 
    tags=["Users"]
)
app.include_router(
    routines.router, 
    prefix=f"{settings.API_V1_STR}/routines", 
    tags=["Routines & Tasks"]
)
app.include_router(
    progress.router, 
    prefix=f"{settings.API_V1_STR}/progress", 
    tags=["Progress Tracking"]
)
app.include_router(
    whatsapp.router, 
    prefix=f"{settings.API_V1_STR}/whatsapp", 
    tags=["WhatsApp Integration"]
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the ScorchTrack API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        reload=False 
    )