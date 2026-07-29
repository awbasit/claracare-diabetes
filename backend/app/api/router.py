from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/doctor")
async def list_doctors() -> list[dict]:
    """Placeholder endpoint — scaffolding only, no business logic yet."""
    return []
