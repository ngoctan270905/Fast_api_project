# Kế hoạch Triển khai Rate Limiting

Tài liệu này hướng dẫn chi tiết cách tích hợp chức năng Rate Limiting (giới hạn tần suất truy cập) vào dự án FastAPI, sử dụng thư viện `slowapi`.

## 1. Giới thiệu và Chiến lược

### Tại sao cần Rate Limiting?
Rate Limiting là một cơ chế phòng thủ thiết yếu cho bất kỳ API nào. Nó giúp:
- **Chống lại tấn công Brute-force**: Ngăn chặn kẻ xấu thử đăng nhập liên tục với các mật khẩu khác nhau.
- **Bảo vệ tài nguyên hệ thống**: Tránh một số người dùng lạm dụng, gửi quá nhiều yêu cầu làm quá tải server.
- **Đảm bảo tính công bằng**: Cung cấp chất lượng dịch vụ ổn định và công bằng cho tất cả người dùng.

### Chiến lược được chọn: `slowapi`
Chúng ta sẽ sử dụng thư viện `slowapi` vì những lý do sau:
- **Tích hợp hoàn hảo**: Được thiết kế để hoạt động với Starlette và FastAPI.
- **Sử dụng Redis**: Tận dụng hạ tầng Redis đã có sẵn trong dự án để lưu trữ và theo dõi số lần truy cập, giúp hệ thống có thể mở rộng (scale) trên nhiều server mà không gặp vấn đề.
- **Linh hoạt**: Cho phép áp dụng giới hạn chung cho toàn bộ API và giới hạn riêng cho từng endpoint cụ thể.

## 2. Hướng dẫn Triển khai Từng bước

### Bước 1: Cài đặt `slowapi`

Đầu tiên, chúng ta cần cài đặt thư viện.

```bash
# Chạy lệnh này trong terminal của bạn
pip install slowapi
```

Sau đó, đừng quên thêm `slowapi==<version>` (ví dụ `slowapi==0.0.14`) vào file `requirements.txt` của bạn để đảm bảo môi trường lập trình nhất quán.

### Bước 2: Cấu hình Rate Limiting

Chúng ta sẽ tập trung logic cấu hình vào các file riêng để giữ cho dự án gọn gàng.

#### 2.1. Cập nhật file cấu hình `app/core/config.py`

Thêm các thiết lập rate limit vào class `Settings`. Điều này cho phép chúng ta thay đổi các giá trị từ file `.env` mà không cần sửa code.

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    # ... (giữ nguyên các cấu hình khác)

    # Cấu hình cài đặt Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # --- THÊM CÁC DÒNG SAU ---
    # Cấu hình Rate Limit
    RATE_LIMIT_ENABLED: bool = True  # Bật/tắt tính năng rate limit
    RATE_LIMIT_DEFAULT: str = "100/minute"  # Giới hạn mặc định cho toàn bộ API
    RATE_LIMIT_AUTH: str = "10/minute"  # Giới hạn chặt hơn cho các endpoint xác thực

    @computed_field
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

```

#### 2.2. Tạo file `app/core/rate_limiter.py`

File này sẽ khởi tạo và cấu hình đối tượng `Limiter` trung tâm.

```python
# app/core/rate_limiter.py

import logging
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Lấy logger
logger = logging.getLogger(__name__)

# Tạo một đối tượng Limiter.
# - key_func: Hàm để xác định định danh của người dùng.
#   Ở đây chúng ta dùng `get_remote_address` để lấy địa chỉ IP của client.
# - enabled: Bật/tắt dựa trên cấu hình trong settings.
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri=settings.REDIS_URL,  # Chỉ định Redis làm nơi lưu trữ
    strategy="fixed-window"  # Sử dụng chiến lược cửa sổ cố định
)

# Ghi log trạng thái của limiter khi ứng dụng khởi động
if settings.RATE_LIMIT_ENABLED:
    logger.info(f"Rate limiting is enabled. Default limit: {settings.RATE_LIMIT_DEFAULT}")
else:
    logger.info("Rate limiting is disabled.")

```

### Bước 3: Tích hợp vào ứng dụng FastAPI

Bây giờ, chúng ta sẽ kết nối `Limiter` với ứng dụng FastAPI trong `app/main.py`.

```python
# app/main.py

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.lifespan import lifespan

# --- THÊM CÁC DÒNG IMPORT SAU ---
from app.core.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded

# --- (giữ nguyên phần logging) ---
logger = logging.getLogger(__name__)

app = FastAPI(title="Library API", lifespan=lifespan)

# --- THÊM CÁC DÒNG SAU ĐỂ XỬ LÝ KHI VƯỢT QUÁ GIỚI HẠN ---

# Gán limiter vào state của app để các decorator có thể truy cập
app.state.limiter = limiter

# Thêm một exception handler để trả về lỗi 429 Too Many Requests một cách thân thiện
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Xử lý ngoại lệ khi một yêu cầu vượt quá giới hạn.
    """
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )

# --- (giữ nguyên phần middleware khác) ---

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# ...

app.add_middleware(LoggingMiddleware)

# Thêm router API
app.include_router(api_router, prefix="/api/v1")
```

### Bước 4: Áp dụng Rate Limiting

Chúng ta sẽ áp dụng rate limit ở hai cấp độ: toàn cục và cho từng endpoint cụ thể.

#### 4.1. Giới hạn Toàn cục (Global Rate Limit)

Cách tốt nhất để áp dụng giới hạn cho mọi request là thông qua một decorator cho router chính. Sửa file `app/api/v1/router.py`.

```python
# app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, books,
    authors, categories, uploads, social_auth
)

# --- THÊM CÁC DÒNG IMPORT SAU ---
from app.core.rate_limiter import limiter
from app.core.config import settings
from fastapi import Depends

# Khởi tạo router chính cho API version 1
api_router = APIRouter()

# --- THÊM DECORATOR VÀO ROUTER ---
# Áp dụng rate limit mặc định cho tất cả các endpoint trong router này.
# slowapi sẽ tự động áp dụng decorator này cho mọi route được include bên dưới.
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def limit_all_requests(request: object): # Cần một hàm async dummy
    pass

api_router.dependencies.append(Depends(limit_all_requests))


# Bao gồm các router con từ các endpoint khác nhau
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(books.router, prefix="/books", tags=["Books"])
api_router.include_router(authors.router, prefix="/authors", tags=["Authors"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_router.include_router(social_auth.router, prefix="/social", tags=["Social Auth"])
```

#### 4.2. Giới hạn Cụ thể cho Endpoint Xác thực

Để tăng cường bảo mật, chúng ta sẽ áp dụng một giới hạn chặt hơn cho các endpoint `login` và `register`. Sửa file `app/api/v1/endpoints/auth.py`.

```python
# app/api/v1/endpoints/auth.py

from typing import Annotated, Optional
# ... (giữ nguyên các import khác)

# --- THÊM CÁC DÒNG IMPORT SAU ---
from app.core.rate_limiter import limiter
from app.core.config import settings
from fastapi import Request

router = APIRouter()

# ==================== REGISTER ====================
# --- THÊM DECORATOR VÀO ĐÂY ---
# Áp dụng giới hạn chặt hơn cho việc đăng ký
# Decorator này sẽ ghi đè giới hạn mặc định đã áp dụng ở router chính.
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
        request: Request, # Thêm request vào hàm để slowapi có thể truy cập
        user_data: UserRegister,
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Register a new user.
    """
    return await auth_service.register(user_data)

# ... (giữ nguyên các endpoint khác như verify-email, forgot-password)

# ==================== LOGIN ====================
# --- THÊM DECORATOR VÀO ĐÂY ---
# Áp dụng giới hạn chặt hơn cho việc đăng nhập để chống brute-force
@router.post("/login", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request, # Thêm request vào hàm để slowapi có thể truy cập
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)]
):
    """
    Log in with OAuth2PasswordRequestForm.
    """
    return await auth_service.login(
        response=response,
        token_service=token_service,
        username=form_data.username,
        password=form_data.password
    )

# ... (giữ nguyên các phần còn lại của file)
```

**Lưu ý quan trọng**: Khi thêm decorator `@limiter.limit`, bạn cần phải thêm `request: Request` làm tham số cho hàm endpoint để `slowapi` có thể hoạt động.

## 3. Tổng kết và Cách kiểm tra

### Tóm tắt các thay đổi:
1.  **Cài đặt `slowapi`** và thêm vào `requirements.txt`.
2.  **Cập nhật `Settings`**: Thêm các biến cấu hình cho rate limit.
3.  **Tạo `rate_limiter.py`**: Khởi tạo `Limiter` trung tâm, kết nối với Redis.
4.  **Tích hợp vào `main.py`**: Thêm `exception_handler` để xử lý lỗi `429 Too Many Requests`.
5.  **Áp dụng giới hạn**:
    - Thêm decorator vào router chính (`api_router`) để áp dụng giới hạn toàn cục.
    - Thêm decorator vào các endpoint nhạy cảm (`/login`, `/register`) với giới hạn chặt hơn.

### Cách kiểm tra:
Bạn có thể dùng một vòng lặp `curl` đơn giản trong terminal để kiểm tra. Ví dụ, để kiểm tra endpoint `/login` với giới hạn `10/phút`:

```bash
# Gửi 11 yêu cầu POST liên tục tới endpoint /login
# Bạn sẽ thấy các yêu cầu đầu tiên thành công (hoặc trả lỗi 401/422 nếu dữ liệu sai)
# và yêu cầu thứ 11 sẽ trả về lỗi 429 Too Many Requests.

for i in {1..11}; do
    echo "Request $i"
    curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=test@example.com&password=wrongpassword" \
         -w "\nStatus: %{http_code}\n\n"
    sleep 1 # Đợi 1 giây giữa các lần gọi
done
```

```