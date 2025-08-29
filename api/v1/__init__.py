from fastapi import APIRouter
from api.v1.endpoints import services, appointments

router = APIRouter()
# Backward compatibility for old endpoint
router.include_router(services.router_biz_services, tags=["services"])
# Appointments endpoint
router.include_router(appointments.router, tags=["appointments"])