from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response


async def request_id_middleware(request: Request, call_next):
    # Extract the mandatory x-request-id header
    request_id = request.headers.get("x-request-id")
    
    # If x-request-id is not provided, raise an HTTPException
    if not request_id:
        raise HTTPException(status_code=400, detail="x-request-id header is required")
    
    # Add the request_id to the request state so it can be accessed by endpoints
    request.state.request_id = request_id
    
    # Call the next middleware/route handler
    response = await call_next(request)
    
    # Add the request_id to the response headers for traceability
    response.headers["x-request-id"] = request_id
    
    return response


# Custom exception handler to ensure CORS headers are added to error responses
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    response = await http_exception_handler(request, exc)
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Custom exception handler to return 400 instead of 422 for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Create a response with 400 status code instead of 422
    response = Response(
        content="Validation error: Invalid request data",
        status_code=400,
        headers={"Content-Type": "text/plain"}
    )
    
    # Add CORS headers if origin is present
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response