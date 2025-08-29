from pydantic import Field
from datetime import datetime
from typing import Optional
from .base import BaseSchema, DateTimeModelMixin
from beanie import PydanticObjectId

class AppointmentBase(BaseSchema):
    customer_name: str
    phone_no: str
    service_id: PydanticObjectId
    appointment_time: datetime
    notes: str | None = None
    tenant_id: str | None = None

class AppointmentCreate(AppointmentBase):
    # Optional field for service name validation
    service_name: str | None = None

class AppointmentUpdate(AppointmentBase):
    status: str

class AppointmentOut(AppointmentBase, DateTimeModelMixin):
    id: PydanticObjectId
    status: str
    booking_number: str
    