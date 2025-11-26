import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


app = FastAPI(
    title="Library API",
)

# Add SessionMiddleware
# This is required by Authlib to store state and other data in the session.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Default Vite port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the logging middleware (should be one of the first)
app.add_middleware(LoggingMiddleware)

# Include router version 1
app.include_router(api_router, prefix="/api/v1")