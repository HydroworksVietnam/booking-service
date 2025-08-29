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
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://h5.zadn.vn",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def options_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=200, content="")
    return await call_next(request)

app.include_router(api_router, prefix=API_VERSION)

# For running the app directly
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=PORT, reload=True)