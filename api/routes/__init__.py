from fastapi import APIRouter
from .scrape import router as scrape_router

router = APIRouter()

router.include_router(scrape_router)
