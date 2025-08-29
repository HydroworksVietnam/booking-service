from fastapi import APIRouter, Query, HTTPException, File, UploadFile, Form
from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Query, File, UploadFile
from models.service import Service
from schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from utils.response import create_response, create_pagination_response
import re

# URL pattern validation
URL_PATTERN = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[-\w./?%&=]*$')

# Backward compatibility router
router_biz_services = APIRouter(prefix="/biz-services")

@router_biz_services.get("")
async def get_services(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")
):
    # Calculate total elements
    total_elements = await Service.find_all().count()
    
    # Get paginated items
    services = await Service.find_all().skip(skip).limit(limit).to_list()
    
    # Create pagination response
    content = [ServiceOut.from_orm(service) for service in services]
    return create_pagination_response(
        content=content,
        total_elements=total_elements,
        page=skip,
        size=limit
    )

@router_biz_services.get("{service_id}")
async def get_service(service_id: PydanticObjectId):
    service = await Service.get(service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    return create_response(ServiceOut.from_orm(service))

@router_biz_services.post("/new")
async def create_service(service: ServiceCreate):
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
    return create_response(ServiceOut.from_orm(new_service), "201")


@router_biz_services.post("/upload/{service_id}")
async def upload_service_images(
    service_id: PydanticObjectId,
    photos: List[UploadFile] = File(None),
    videos: List[UploadFile] = File(None)
):
    service = await Service.get(service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    
    # In a real application, you would save these files to storage
    # and add their URLs to the service
    
    # For demonstration purposes, we'll just return the filenames
    photo_filenames = [photo.filename for photo in photos] if photos else []
    video_filenames = [video.filename for video in videos] if videos else []
    
    return create_response({
        "message": "Files uploaded successfully",
        "photos": photo_filenames,
        "videos": video_filenames
    })

@router_biz_services.post("/image/upload")
async def upload_service_image(file: UploadFile = File(...)):
    async with httpx.AsyncClient() as client:
        files = {"file": (file.filename, file.file, file.content_type)}
        response = await client.post("http://localhost:6000/upload", files=files)
        return response.json()

@router_biz_services.put("/{service_id}")
async def update_service(service_id: PydanticObjectId, service: ServiceUpdate):
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
    return create_response(ServiceOut.from_orm(db_service))

@router_biz_services.delete("/{service_id}")
async def delete_service(service_id: PydanticObjectId):
    service = await Service.get(service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
    await service.delete()
    return create_response(None, "204")