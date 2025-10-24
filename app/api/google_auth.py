from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config as StarletteConfig

from ..database import get_db
from ..models import User
from ..core.security import create_access_token, hash_password
from ..core.config import settings

router = APIRouter(prefix="/auth/google", tags=["auth"])

starlette_config = StarletteConfig(environ={
    "GOOGLE_CLIENT_ID": settings.google_client_id or "",
    "GOOGLE_CLIENT_SECRET": settings.google_client_secret or "",
})
oauth = OAuth(starlette_config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        # opcjonalnie włącz PKCE: "code_challenge_method": "S256"
    },
)

@router.get("/login")
async def google_login(request: Request):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    redirect_uri = f"{settings.server_base_url}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        if not userinfo:
            # jeżeli provider nie zwrócił userinfo, pobierz jawnie
            resp = await oauth.google.get("userinfo", token=token)
            userinfo = resp.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")

    email = (userinfo.get("email") or "").lower()
    if not email:
        raise HTTPException(status_code=400, detail="Brak e-maila z Google")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        import secrets
        random_password = secrets.token_urlsafe(24)
        user = User(
            email=email,
            hashed_password=hash_password(random_password),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Konto zablokowane")

    access_token = create_access_token(subject=user.email)

    html = f"""
    <html><body>
      <script>
        try {{
          localStorage.setItem('access_token', {access_token!r});
          window.location.href = '/';
        }} catch(e) {{
          // fallback: przekierowanie z tokenem w query (gdy localStorage zablokowane)
          window.location.href = '/?token=' + encodeURIComponent({access_token!r});
        }}
      </script>
      Logowanie zakończone. Jeżeli nie nastąpi przekierowanie, <a href="/">kliknij tutaj</a>.
    </body></html>
    """
    return HTMLResponse(content=html)