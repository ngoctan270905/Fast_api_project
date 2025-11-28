import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.lifespan import lifespan

logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Library API", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix="/api/v1")