from fastapi import APIRouter
from .scrape import router as scrape_router
from .health import router as health_router

router = APIRouter()

router.include_router(scrape_router)
router.include_router(health_router, prefix="/health")
