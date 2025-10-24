from fastapi import APIRouter

from .categories import router as categories_router
from .transactions import router as transactions_router
from .reports import router as reports_router
from .debug import router as debug_router

# Auth is optional during development: keep the rest of API working even if auth deps are missing
try:
    from .auth import router as auth_router  # type: ignore
except Exception:
    auth_router = None  # type: ignore

try:
    from .google_auth import router as google_auth_router  # type: ignore
except Exception:
    google_auth_router = None  # type: ignore

router = APIRouter()

# Core public routers
router.include_router(categories_router)
router.include_router(transactions_router)
router.include_router(reports_router)
router.include_router(debug_router)

# Optional routers
if auth_router is not None:
    router.include_router(auth_router)
if google_auth_router is not None:
    router.include_router(google_auth_router)
