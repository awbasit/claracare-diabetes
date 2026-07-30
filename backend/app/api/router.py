from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.patients.router import router as patients_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(patients_router)


@api_router.get("/doctor")
async def list_doctors() -> list[dict]:
    """Placeholder endpoint — scaffolding only, no business logic yet."""
    return []
