### Kế hoạch tích hợp Đăng nhập bằng Facebook

Để thêm chức năng đăng nhập bằng Facebook, chúng ta sẽ thực hiện các bước tương tự như đã làm với Google và GitHub.

#### 1. Cập nhật Cấu hình (`.env` và `config.py`)

Thêm `FACEBOOK_CLIENT_ID` và `FACEBOOK_CLIENT_SECRET` vào file `.env` và `library_api/app/core/config.py`.

-   **File**: `library_api/.env`
    ```
    FACEBOOK_CLIENT_ID=your_facebook_app_id
    FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
    ```
-   **File**: `library_api/app/core/config.py`
    Thêm các dòng sau vào trong class `Settings`:
    ```python
    # Facebook OAuth Settings
    FACEBOOK_CLIENT_ID: str
    FACEBOOK_CLIENT_SECRET: str
    ```

#### 2. Đăng ký Facebook OAuth Provider (`oauth.py`)

Đăng ký client Facebook với `authlib`.

-   **File**: `library_api/app/core/oauth.py`
    Thêm vào cuối file:
    ```python
    oauth.register(
        name='facebook',
        client_id=settings.FACEBOOK_CLIENT_ID,
        client_secret=settings.FACEBOOK_CLIENT_SECRET,
        authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
        access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email public_profile'},
    )
    ```

#### 3. Thêm Logic xử lý OAuth trong `AuthService` (`auth_service.py`)

Tạo một phương thức mới `handle_facebook_oauth` để xử lý callback từ Facebook.

-   **File**: `library_api/app/services/auth_service.py`
    Thêm phương thức sau vào class `AuthService`:
    ```python
    async def handle_facebook_oauth(self, request: Request) -> str:
        """
        Handles the Facebook OAuth callback, creates/updates the user, and returns a JWT.
        """
        try:
            token = await oauth.facebook.authorize_access_token(request)
            resp = await oauth.facebook.get(
                'me?fields=id,name,email,picture',
                token=token
            )
            resp.raise_for_status()
            user_info = resp.json()

            facebook_account_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name')

            if not email or not facebook_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve essential user information from Facebook."
                )

            user = await self.user_repo.find_or_create_by_oauth(
                provider="facebook",
                account_id=facebook_account_id,
                email=email,
                username=name or email.split('@')[0]
            )
            
            access_token = create_access_token(
                data={"sub": str(user.id), "username": user.username}
            )
            
            return access_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Facebook authentication failed: {e}"
            )
    ```

#### 4. Thêm API Endpoints (`social_auth.py`)

Tạo các endpoint để bắt đầu quá trình đăng nhập và xử lý callback.

-   **File**: `library_api/app/api/v1/endpoints/social_auth.py`
    Thêm vào cuối file:
    ```python
    @router.get("/login/facebook")
    async def login_facebook(request: Request):
        """
        Redirects to Facebook's OAuth login page.
        """
        redirect_uri = request.url_for('auth_facebook_callback')
        return await oauth.facebook.authorize_redirect(request, redirect_uri)

    @router.get("/auth/facebook/callback", name="auth_facebook_callback")
    async def auth_facebook_callback(
        request: Request,
        auth_service: AuthService = Depends(get_auth_service)
    ):
        """
        Handles the callback from Facebook after user authentication.
        """
        access_token = await auth_service.handle_facebook_oauth(request)
        
        redirect_url = f"{settings.CLIENT_BASE_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
    ```
