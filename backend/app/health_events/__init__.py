# Importing the glucose service module registers it with health_event_service's
# dispatch registry (EventType.glucose -> GlucoseService) as a side effect.
# Anything importing a health_events submodule imports this package first, so
# the registration always happens before health_event_service is used.
from app.health_events.glucose import service as _glucose_service  # noqa: F401
