from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Request, Response, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from core.database import init_db
from core.middleware import request_id_middleware, custom_http_exception_handler, validation_exception_handler
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables with default values
PROJECT_NAME = os.getenv('PROJECT_NAME', 'Booking Service')
API_VERSION = os.getenv('API_VERSION', '/api/v1')
PORT = int(os.getenv('PORT', '9800'))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title=PROJECT_NAME, lifespan=lifespan, redirect_slashes=False)

# Configure CORS
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000,https://h5.zadn.vn')

# Register custom exception handlers
app.exception_handler(HTTPException)(custom_http_exception_handler)
app.exception_handler(RequestValidationError)(validation_exception_handler)

app.middleware("http")(request_id_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_origin_regex="https?://.*",
    expose_headers=["Access-Control-Allow-Origin", "Accept"]
)

app.include_router(api_router, prefix=API_VERSION)

# For running the app directly
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=PORT, reload=True)