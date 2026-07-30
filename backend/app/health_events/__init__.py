# Importing each type's service module registers it with health_event_service's
# dispatch registry (EventType.x -> XService) as a side effect. Anything
# importing a health_events submodule imports this package first, so
# registration always happens before health_event_service is used.
from app.health_events.exercise import service as _exercise_service  # noqa: F401
from app.health_events.glucose import service as _glucose_service  # noqa: F401
from app.health_events.meals import service as _meals_service  # noqa: F401
from app.health_events.medication_log import service as _medication_log_service  # noqa: F401
from app.health_events.sleep import service as _sleep_service  # noqa: F401
from app.health_events.stress import service as _stress_service  # noqa: F401
from app.health_events.symptoms import service as _symptoms_service  # noqa: F401
from app.health_events.vitals import service as _vitals_service  # noqa: F401
