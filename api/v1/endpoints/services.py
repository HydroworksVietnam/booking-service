from fastapi import APIRouter, Query, HTTPException, File, UploadFile, Form, Request
from typing import List, Optional
from beanie import PydanticObjectId
from models.service import Service
from schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from utils.response import create_response, create_pagination_response
import re
from services.image_service import upload_images

# URL pattern validation
URL_PATTERN = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[-\w./?%&=]*$')

# Backward compatibility router
router_biz_services = APIRouter(prefix="/biz-services")

@router_biz_services.get("")
async def get_services(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    # Calculate total elements
    total_elements = await Service.find_all().count()
    
    # Get paginated items
    services = await Service.find_all().skip(skip).limit(limit).to_list()
    
    # Calculate page number (1-indexed) from skip and limit
    # If skip=0, page=1; if skip=5 and limit=5, page=2, etc.
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Create pagination response
    content = [ServiceOut.from_orm(service) for service in services]
    return create_pagination_response(
        content=content,
        total_elements=total_elements,
        page=page,
        size=limit,
        request_id=request_id
    )

@router_biz_services.get("{service_id}")
async def get_service(
    request: Request,
    service_id: PydanticObjectId
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    service = await Service.get(service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    return create_response(ServiceOut.from_orm(service), request_id=request_id)

@router_biz_services.post("/new")
async def create_service(
    request: Request,
    service: ServiceCreate
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    # Validate photo and video URLs if provided
    for photo in service.photos:
        if not URL_PATTERN.match(photo):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid photo URL format: {photo}"
            )
    
    for video in service.videos:
        if not URL_PATTERN.match(video):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video URL format: {video}"
            )
    
    # Create service without extra fields by using exclude_unset
    new_service = Service(**service.dict(exclude_unset=True))
    await new_service.save()
    return create_response(ServiceOut.from_orm(new_service), "201", request_id)

@router_biz_services.post("/image/upload")
async def upload_service_image(
    request: Request,
    category: str = Form(...),
    files: List[UploadFile] = File(...)
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    result = await upload_images(category, files)
    return create_response(result, request_id=request_id)

@router_biz_services.put("/{service_id}")
async def update_service(
    request: Request,
    service_id: PydanticObjectId, 
    service: ServiceUpdate
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    db_service = await Service.get(service_id)
    if not db_service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    # Use exclude_unset to ensure we only update provided fields and ignore extras
    update_data = service.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)
    await db_service.save()
    return create_response(ServiceOut.from_orm(db_service), request_id=request_id)

@router_biz_services.delete("/{service_id}")
async def delete_service(
    request: Request,
    service_id: PydanticObjectId
):
    # Get the request_id from the request state (added by middleware)
    request_id = request.state.request_id
    
    service = await Service.get(service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    await service.delete()
    return create_response(None, "204", request_id)