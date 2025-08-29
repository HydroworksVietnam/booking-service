import os
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:8001')

async def get_user_by_id(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return response.json()