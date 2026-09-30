from fastapi import APIRouter
from backend.app.api import videos, analysis, athletes, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(videos.router)
api_router.include_router(analysis.router)
api_router.include_router(athletes.router)
