from fastapi import APIRouter

from .categories import router as categories_router
from .transactions import router as transactions_router
from .reports import router as reports_router
from .debug import router as debug_router

router = APIRouter()

router.include_router(categories_router)
router.include_router(transactions_router)
router.include_router(reports_router)
router.include_router(debug_router)


