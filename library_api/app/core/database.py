# app/core/database.py
import os
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from dotenv import load_dotenv

# 🔹 Load biến môi trường
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA {DATABASE_URL}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được thiết lập trong .env")

# 🔹 Tạo Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,           # True để log SQL (debug)
    future=True
)

# Tạo async session maker - tạo ra các phiên kết nối database bất đồng bộ
async_sessionmaker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency để inject session vào endpoint
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session

