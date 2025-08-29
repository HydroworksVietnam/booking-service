from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import Field, validator
from models.appointment import Appointment
from models.service import Service
from schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from utils.response import create_response, create_pagination_response

router = APIRouter(prefix="/bookings")

@router.get("")
async def get_appointments(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=1000), tenant_id: Optional[str] = None):
    # Filter appointments based on provided parameters
    query = {}
    # if user_id:
    #     query["user_id"] = user_id
    if tenant_id:
        query["tenant_id"] = tenant_id

    # Calculate total elements
    total_elements = await Appointment.find(query).count()
    
    # Get paginated items
    appointments = await Appointment.find(query).skip(skip).limit(limit).to_list()
    
    # Create pagination response
    content = [AppointmentOut.from_orm(appt) for appt in appointments]
    return create_pagination_response(
        content=content,
        total_elements=total_elements,
        page=skip,
        size=limit
    )

@router.get("/{appointment_id}")
async def get_appointment(appointment_id: PydanticObjectId):
    appointment = await Appointment.get(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    return create_response(AppointmentOut.from_orm(appointment))

@router.post("/new")
async def create_appointment(appointment: AppointmentCreate):
    # Check if service exists
    service = await Service.get(appointment.service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    
    # Validate service name if provided
    if appointment.service_name:
        # Strip whitespace and convert to lowercase for case-insensitive comparison
        requested_name = appointment.service_name.strip().lower()
        actual_name = service.name.strip().lower()
        if requested_name != actual_name:
            raise HTTPException(
                status_code=400,
                detail=f"Service name '{appointment.service_name}' does not match the service with ID {appointment.service_id}"
            )
    # Check if appointment time is in the future
    # Use offset-aware datetime for comparison
    if appointment.appointment_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Appointment time must be in the future"
        )
    # Check for overlapping appointments
    # overlapping_appointment = await Appointment.find_one(
    #     Appointment.appointment_time == appointment.appointment_time,
    #     Appointment.status == "scheduled"
    # )
    # if overlapping_appointment:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="This time slot is already booked"
    #     )
    # Create new appointment
    new_appointment = Appointment(
        customer_name=appointment.customer_name,
        phone_no=appointment.phone_no,
        service_id=appointment.service_id,
        tenant_id=appointment.tenant_id,
        appointment_time=appointment.appointment_time,
        status="Pending",
        notes=appointment.notes
    )
    saved_appointment = await new_appointment.save()
    return create_response(AppointmentOut.from_orm(saved_appointment), "201")

@router.put("/{appointment_id}")
async def update_appointment(appointment_id: PydanticObjectId, appointment: AppointmentUpdate, tenant_id: Optional[str] = None):
    db_appointment = await Appointment.get(appointment_id)
    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    # Check if tenant is allowed to update this appointment
    if tenant_id and db_appointment.tenant_id != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to update appointments from other tenants"
        )
    # If changing appointment time, check if it's in the future
    if appointment.appointment_time and appointment.appointment_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Appointment time must be in the future"
        )
    # Update appointment fields
    if appointment.service_id:
        service = await Service.get(appointment.service_id)
        if not service:
            raise HTTPException(
                status_code=404,
                detail="Service not found"
            )
        db_appointment.service_id = appointment.service_id
    if appointment.appointment_time:
        db_appointment.appointment_time = appointment.appointment_time
    if appointment.status:
        db_appointment.status = appointment.status
    if appointment.notes is not None:
        db_appointment.notes = appointment.notes
    if appointment.tenant_id is not None:
        db_appointment.tenant_id = appointment.tenant_id

    await db_appointment.save()
    return create_response(AppointmentOut.from_orm(db_appointment))

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: PydanticObjectId, tenant_id: Optional[str] = None):
    appointment = await Appointment.get(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    # Check if tenant is allowed to delete this appointment
    if tenant_id and appointment.tenant_id != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to delete appointments from other tenants"
        )
    # Instead of deleting, mark it as canceled (recommended approach)
    appointment.status = "canceled"
    await appointment.save()
    return create_response(None, "204")