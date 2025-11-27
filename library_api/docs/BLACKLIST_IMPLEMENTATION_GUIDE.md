# Hướng dẫn Triển khai Token Blacklist với Redis

Tài liệu này cung cấp một kế hoạch chi tiết và chuyên nghiệp để triển khai tính năng Token Blacklist cho các JWT access token, sử dụng Redis làm nơi lưu trữ.

---

## 1. Mục tiêu

Mục tiêu chính là cho phép hệ thống có khả năng **vô hiệu hóa ngay lập tức một `access_token`** đã được cấp, ngay cả khi token đó chưa hết hạn. Điều này cực kỳ quan trọng trong các trường hợp:
-   Người dùng chủ động đăng xuất (`logout`).
-   Người dùng đổi mật khẩu.
-   Quản trị viên khóa tài khoản người dùng.

Việc này ngăn chặn tình huống token bị đánh cắp và tiếp tục được sử dụng để truy cập tài nguyên một cách trái phép.

---

## 2. Công nghệ Đề xuất

-   **Redis:** Một hệ quản trị cơ sở dữ liệu key-value trong bộ nhớ (in-memory), nổi tiếng với tốc độ truy xuất cực nhanh. Redis là lựa chọn lý tưởng cho việc xây dựng blacklist vì:
    -   Tốc độ kiểm tra (lookup) một token có trong blacklist hay không gần như tức thời, không làm ảnh hưởng đến hiệu suất của request.
    -   Hỗ trợ cơ chế tự hết hạn (Time To Live - TTL), cho phép chúng ta tự động xóa các token ID đã hết hạn khỏi blacklist, giữ cho blacklist luôn gọn nhẹ.

---

## 3. Các bước Triển khai Chi tiết

Dưới đây là các bước để tích hợp tính năng này vào dự án một cách hoàn chỉnh.

### Bước 1: Cài đặt và Cấu hình

1.  **Cài đặt Redis Server:** Đảm bảo bạn đã có một Redis server đang chạy. Bạn có thể cài đặt qua Docker hoặc trực tiếp trên máy.
2.  **Thêm thư viện vào `requirements.txt`:**
    ```
    redis
    ```
    Sau đó chạy `pip install -r requirements.txt`.
3.  **Thêm cấu hình vào `.env` và `config.py`:**
    -   Trong file `.env`, thêm các dòng sau:
        ```env
        REDIS_HOST=localhost
        REDIS_PORT=6379
        REDIS_DB=0
        ```
    -   Trong file `library_api/app/core/config.py`, trong class `Settings`, thêm các biến tương ứng:
        ```python
        # Redis Settings
        REDIS_HOST: str = "localhost"
        REDIS_PORT: int = 6379
        REDIS_DB: int = 0
        ```

### Bước 2: Tạo Module Kết nối Redis

Tạo một file mới `library_api/app/core/redis_client.py` để quản lý kết nối.

```python
# library_api/app/core/redis_client.py
import redis.asyncio as redis
from app.core.config import settings

# Tạo một connection pool để tái sử dụng kết nối, tăng hiệu suất
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True  # Tự động decode responses từ bytes sang string
)

def get_redis_client() -> redis.Redis:
    """
    Dependency to get a Redis client from the connection pool.
    """
    return redis.Redis(connection_pool=redis_pool)
```

### Bước 3: Cập nhật Hàm tạo Access Token (`security.py`)

Cần đảm bảo mỗi `access_token` có một định danh duy nhất (`jti`).

-   Trong `library_api/app/core/security.py`, cập nhật hàm `create_access_token`:
    ```python
    import uuid # Thêm import này ở đầu file

    # ...

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "scope": "access_token",
            "jti": str(uuid.uuid4())  # Thêm dòng này
        })

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    ```

### Bước 4: Tạo Blacklist Service

Tạo một service chuyên dụng `library_api/app/services/blacklist_service.py`.

```python
# library_api/app/services/blacklist_service.py
from datetime import timedelta
import redis.asyncio as redis

class BlacklistService:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def add_to_blacklist(self, jti: str, expires_in: timedelta):
        """
        Thêm JTI của token vào blacklist với thời gian sống bằng thời gian còn lại của token.
        Key trong Redis sẽ là `jti:{jti_value}` để dễ quản lý.
        """
        key = f"jti:{jti}"
        await self.redis_client.setex(name=key, time=expires_in, value="blacklisted")

    async def is_blacklisted(self, jti: str) -> bool:
        """
        Kiểm tra xem một JTI có nằm trong blacklist hay không.
        """
        key = f"jti:{jti}"
        return await self.redis_client.exists(key)
```

### Bước 5: Tái cấu trúc và Tích hợp Blacklist vào Luồng Xác thực



Để có một kiến trúc trong sạch và dễ bảo trì, chúng ta sẽ **tái cấu trúc** lại logic xác thực token. Thay vì kiểm tra blacklist bên trong `get_current_user`, chúng ta sẽ chuyển toàn bộ logic xác thực—bao gồm cả kiểm tra blacklist—vào trong hàm `verify_scoped_token`.



Cách tiếp cận này giúp **đóng gói** toàn bộ trách nhiệm xác thực token vào một nơi duy nhất (`security.py`), giúp `dependencies.py` trở nên đơn giản và chỉ tập trung vào việc lấy dữ liệu.



#### 5.1. Cập nhật `verify_scoped_token` trong `app/core/security.py`



Hàm `verify_scoped_token` sẽ được chuyển thành `async`, nhận thêm `redis_client`, và thực hiện kiểm tra blacklist.



```python

# app/core/security.py



# ... (thêm các import cần thiết ở đầu file)

import redis.asyncio as redis

from app.services.blacklist_service import BlacklistService



# ...



async def verify_scoped_token(token: str, required_scope: str, redis_client: redis.Redis) -> str:

    """

    Xác thực một JWT, kiểm tra chữ ký, thời gian hết hạn, scope, và trạng thái blacklist.

    """

    credentials_exception = HTTPException(

        status_code=status.HTTP_401_UNAUTHORIZED,

        detail="Could not validate credentials",

        headers={"WWW-Authenticate": "Bearer"},

    )

    try:

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        

        # Kiểm tra scope và subject

        token_scope = payload.get("scope")

        subject = payload.get("sub")

        if subject is None:

            raise credentials_exception

        if token_scope != required_scope:

            raise HTTPException(

                status_code=status.HTTP_401_UNAUTHORIZED,

                detail=f"Invalid token scope. Required: {required_scope}",

            )



        # === PHẦN THÊM MỚI: KIỂM TRA BLACKLIST ===

        # Chỉ kiểm tra blacklist đối với access_token

        if required_scope == "access_token":

            jti = payload.get("jti")

            if not jti:

                raise JWTError("Token does not have a JTI (JWT ID)")



            blacklist_service = BlacklistService(redis_client)

            if await blacklist_service.is_blacklisted(jti):

                raise HTTPException(

                    status_code=status.HTTP_401_UNAUTHORIZED,

                    detail="Token has been revoked",

                    headers={"WWW-Authenticate": "Bearer"},

                )

        # ==========================================

            

        return subject



    except jwt.ExpiredSignatureError:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Token has expired",

        )

    except JWTError as e:

        # Ném lại lỗi cụ thể nếu có

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=str(e),

            headers={"WWW-Authenticate": "Bearer"},

        )

```



#### 5.2. Đơn giản hóa `get_current_user` trong `app/core/dependencies.py`



Bây giờ, `get_current_user` chỉ cần gọi `verify_scoped_token` đã được nâng cấp và xử lý kết quả.



```python

# app/core/dependencies.py



# ... (các import khác giữ nguyên)

from app.core.security import verify_scoped_token # Đảm bảo đã import

# ...



async def get_current_user(

    token: Annotated[str, Depends(oauth2_scheme)],

    session: DbSession,

    redis_client: Annotated[redis.Redis, Depends(get_redis_client)]

) -> User:

    try:

        # Gọi hàm xác thực đã bao gồm cả check blacklist

        user_id = await verify_scoped_token(

            token=token, 

            required_scope="access_token", 

            redis_client=redis_client

        )

        if not user_id:

            raise JWTError("User ID not in token")



    except HTTPException as e:

        # Ném lại lỗi từ verify_scoped_token

        raise e

    except JWTError as e:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail=f"Invalid token: {e}",

            headers={"WWW-Authenticate": "Bearer"},

        )



    # Lấy thông tin user từ DB

    query = select(User).where(User.id == user_id)

    result = await session.execute(query)

    user = result.scalar_one_or_none()



    if not user:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="User not found",

            headers={"WWW-Authenticate": "Bearer"},

        )

    return user

```

### Bước 6: Cập nhật Luồng Đăng xuất (`auth.py`)

Cập nhật endpoint `/logout` để nó thực sự vô hiệu hóa `access_token` đang được sử dụng.

```python
# Trong library_api/app/api/v1/endpoints/auth.py

# Thêm các import cần thiết
from app.core.redis_client import get_redis_client
from app.services.blacklist_service import BlacklistService
from jose import jwt
from datetime import datetime, timezone

# ...

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
    token: Annotated[str, Depends(oauth2_scheme)],
    refresh_token: Optional[str] = Cookie(None),
):
    """
    Đăng xuất người dùng bằng cách:
    1. Vô hiệu hóa access token (thêm vào blacklist).
    2. Thu hồi refresh token (xóa khỏi DB và cookie).
    """
    # 1. Blacklist the access token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_signature": False, "verify_aud": False, "verify_exp": False})
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            # Tính thời gian còn lại của token
            expires_in = timedelta(seconds=max(0, exp - int(datetime.now(timezone.utc).timestamp())))
            blacklist_service = BlacklistService(redis_client)
            await blacklist_service.add_to_blacklist(jti, expires_in)
    except JWTError:
        # Bỏ qua nếu token không hợp lệ, vì dù sao cũng sẽ logout
        pass

    # 2. Revoke the refresh token (logic cũ)
    if refresh_token:
        await auth_service.logout(
            response=response,
            token_service=token_service,
            refresh_token=refresh_token
        )
    else:
        # Nếu không có refresh token, chỉ cần xóa cookie (nếu có)
        response.delete_cookie(key="refresh_token")

    return {"message": "You have been logged out successfully."}
```

Sau khi hoàn thành các bước trên, hệ thống sẽ có một cơ chế blacklist hoàn chỉnh và an toàn.
