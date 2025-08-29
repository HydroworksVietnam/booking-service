from beanie import PydanticObjectId, Link
from pydantic import Field, BeforeValidator
from .base import BaseDocument
from typing import Optional, Any
from datetime import datetime
from models.service import Service
import random
import string

# Function to generate booking number
def generate_booking_number() -> str:
    # Format: BK-{timestamp}-{random 6 chars}
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BK-{timestamp}-{random_chars}"

class Appointment(BaseDocument):
    customer_name: str
    phone_no: str
    service_id: PydanticObjectId
    appointment_time: datetime
    status: str = Field(default="Pending")  # Pending, completed, canceled
    notes: Optional[str] = None
    tenant_id: Optional[str] = None  # Add tenant_id for authorization
    booking_number: str = Field(default_factory=generate_booking_number, unique=True)  # Unique booking number

    # Relationship with service
    service: Optional[Link[Service]] = None

    class Settings:
        name = "bookings"
        indexes = ["customer_name", "phone_no", "service_id"]
