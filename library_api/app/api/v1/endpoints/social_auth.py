from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_auth_service
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


@router.get("/login/github")
async def login_github(request: Request):
    """
    Redirects to GitHub's OAuth login page.
    """
    redirect_uri = request.url_for('auth_github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/auth/github/callback", name="auth_github_callback")
async def auth_github_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handles the callback from GitHub after user authentication.
    """
    access_token = await auth_service.handle_github_oauth(request)
    
    redirect_url = f"{settings.CLIENT_BASE_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


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
