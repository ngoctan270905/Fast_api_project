from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from jose import JWTError
import re
from typing import Pattern

from app.core.security import verify_scoped_token
from app.repositories.user_repository import UserRepository
from app.core.database import async_sessionmaker

# Những route không cần xác thực middle sẽ bỏ qua
PUBLIC_PATHS: list[Pattern] = [
    re.compile(r"^/docs$"),
    re.compile(r"^/openapi\.json$"),
    re.compile(r"^/api/v1/auth/.*$"),
    re.compile(r"^/api/v1/social-auth/.*$"),
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Chặn request, kiểm tra JWT đối với các route cần bảo vệ,
        và gắn thông tin user vào request.state nếu hợp lệ.
        """

        # Kiểm tra xem route hiện tại có thuộc danh sách public hay không
        for pattern in PUBLIC_PATHS: #PUBLIC_PATHS danh sách palttern công khai
            # kiểm tra đường dẫn có khớp với plattern ko
            if pattern.match(request.url.path):
                # nếu khớp thì sẽ bỏ qua bước xác thực và tiếp tục xử lí request
                return await call_next(request)

        # Nếu ko phải route public thì bắt đầu xác minh
        auth_header = request.headers.get("Authorization")
        # nếu ko có header và ko header ko có dạng beared
        if not auth_header or not auth_header.startswith("Bearer "):
            # trả về lỗi 401
            return JSONResponse(
                status_code=401,
                content={"detail": "Chưa xác thực (Not authenticated)"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        # lấy token từ header
        token = auth_header.split(" ")[1]

        try:
            # Xác minh token. Hàm này sẽ raise exception nếu token sai hoặc hết hạn
            user_id_str = verify_scoped_token(token, required_scope="access_token")

            if not user_id_str:
                raise JWTError("Không tìm thấy user ID (sub) trong token")

            # Tạo session DB để truy vấn user tương ứng
            async with async_sessionmaker() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(int(user_id_str))

            if not user:
                # Token hợp lệ nhưng user đã bị xóa
                raise JWTError("User không tồn tại")

            # Gắn user vào request.state để dùng trong endpoint
            request.state.user = user

        except (JWTError, ValueError) as e:
            # Bắt lỗi token sai, lỗi giải mã, hoặc lỗi parse user_id
            return JSONResponse(
                status_code=401,
                content={"detail": f"Token không hợp lệ: {e}"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Nếu mọi kiểm tra đều OK → cho phép request đi tiếp vào endpoint
        response = await call_next(request)
        return response
