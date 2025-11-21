from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, get_auth_service
from app.core.config import settings
from app.core.oauth import oauth
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("/login/google")
async def login_google(request: Request):
    """
    Redirects to Google's OAuth login page.
    """
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback", name="auth_google_callback")
async def auth_google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handles the callback from Google after user authentication.
    It uses the AuthService to handle the logic and then redirects the user
    to the frontend with the access token.
    """
    access_token = await auth_service.handle_google_oauth(request)
    
    # Redirect user to the frontend with the JWT
    # In a real app, you might use cookies or a more secure redirect flow.
    redirect_url = f"{settings.CLIENT_BASE_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
