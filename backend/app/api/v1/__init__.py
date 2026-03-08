from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.billboards import router as billboards_router
from app.api.v1.check_radius import router as check_radius_router
from app.api.v1.import_billboards import router as import_billboards_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(billboards_router)
router.include_router(check_radius_router)
router.include_router(import_billboards_router)
