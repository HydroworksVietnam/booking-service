from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from core.database import init_db
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
    # Startup event
    await init_db()
    yield
    # Shutdown event (if needed)

app = FastAPI(title=PROJECT_NAME, lifespan=lifespan, redirect_slashes=False)

# Configure CORS
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000,https://h5.zadn.vn')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_origin_regex="https?://.*",
    expose_headers=["Access-Control-Allow-Origin", "Accept"]
)

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Set CORS headers for all responses
    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # For OPTIONS requests, set additional headers
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        allowed_headers = request.headers.get("access-control-request-headers", "*")
        if allowed_headers != "*" and "accept" not in allowed_headers.lower():
            allowed_headers += ", Accept"
        response.headers["Access-Control-Allow-Headers"] = allowed_headers
        response.headers["Access-Control-Max-Age"] = "86400"
        response.status_code = 200
        response.content = ""
    
    return response

app.include_router(api_router, prefix=API_VERSION)

# For running the app directly
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=PORT, reload=True)