from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.schemas.response import ErrorResponse
import logging

logger = logging.getLogger(__name__)

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            status="error",
            message="Too many requests",
            detail=f"Rate limit exceeded: {exc.detail}"
        ).model_dump()
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler cho các lỗi HTTPException được ném ra chủ động từ code FastAPI.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            message=exc.detail,
        ).model_dump(),
        headers=exc.headers
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler cho tất cả các lỗi không xác định (lỗi hệ thống không lường trước).
    """
    logger.error(f"Unhandled error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message="Đã xảy ra lỗi máy chủ không mong muốn",
        ).model_dump()
    )