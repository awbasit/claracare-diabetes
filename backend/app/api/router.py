from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.health_events.exercise.router import router as exercise_router
from app.health_events.glucose.router import router as glucose_router
from app.health_events.meals.router import router as meals_router
from app.health_events.medication_log.router import router as medication_log_router
from app.health_events.sleep.router import router as sleep_router
from app.health_events.stress.router import router as stress_router
from app.health_events.symptoms.router import router as symptoms_router
from app.health_events.vitals.router import router as vitals_router
from app.patients.router import router as patients_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(patients_router)
api_router.include_router(glucose_router)
api_router.include_router(meals_router)
api_router.include_router(medication_log_router)
api_router.include_router(exercise_router)
api_router.include_router(sleep_router)
api_router.include_router(stress_router)
api_router.include_router(symptoms_router)
api_router.include_router(vitals_router)


@api_router.get("/doctor")
async def list_doctors() -> list[dict]:
    """Placeholder endpoint — scaffolding only, no business logic yet."""
    return []
