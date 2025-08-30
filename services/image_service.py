from fastapi import UploadFile, HTTPException
from typing import List
import httpx
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the upload service URL from environment variables
UPLOAD_SERVICE_URL = os.getenv('UPLOAD_SERVICE_URL', 'http://localhost:6000')

async def upload_images(category: str, files: List[UploadFile]):
    # Log incoming files
    logger.info(f"Received {len(files)} files for category: {category}")
    for i, file in enumerate(files):
        logger.info(f"File {i+1}: filename={file.filename}, content_type={file.content_type}")
    
    # Validate files
    for file in files:
        # Check file type
        if not file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only PNG, JPEG, and JPG files are allowed."
            )
        
        # Check file size (4MB limit)
        contents = await file.read()
        await file.seek(0)  # Reset file pointer
        if len(contents) > 4 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds 4MB limit: {len(contents)} bytes"
            )
    
    # Forward files to the image service
    async with httpx.AsyncClient() as client:
        # Prepare files for forwarding
        forwarded_files = []
        for file in files:
            forwarded_files.append(("imageFiles", (file.filename, file.file, file.content_type)))
        
        # Add category to the form data
        form_data = {"category": category}
        
        response = await client.post(
            UPLOAD_SERVICE_URL,
            files=forwarded_files,
            data=form_data
        )
        
        # Check if the upstream service returned an error
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        
        return response.json()