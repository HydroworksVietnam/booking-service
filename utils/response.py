from typing import Generic, TypeVar, Any, List, Optional
import uuid

T = TypeVar('T')

class APIResponse(Generic[T]):
    def __init__(self, payload: T, status_code: str = "200", request_id: Optional[str] = None):
        self.status = status_code
        self.payload = payload
        # Use provided request_id or generate a new one if not provided
        self.meta = {
            "requestId": request_id if request_id else str(uuid.uuid4())
        }

    def dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "payload": self.payload,
            "meta": self.meta
        }

class APIResponsePagination(Generic[T]):
    def __init__(self, content: List[T], total_pages: int, total_elements: int, page: int, size: int, request_id: Optional[str] = None):
        self.content = content
        self.totalPages = total_pages
        self.totalElements = total_elements
        self.page = page
        self.size = size
        self.request_id = request_id

    def dict(self) -> dict[str, Any]:
        result = {
            "content": self.content,
            "totalPages": self.totalPages,
            "totalElements": self.totalElements,
            "page": self.page,
            "size": self.size
        }
        # Include request_id in meta if provided
        if self.request_id:
            result["meta"] = {"requestId": self.request_id}
        return result


def create_response(payload: T, status_code: str = "200", request_id: Optional[str] = None) -> dict[str, Any]:
    """Create a response following the APIResponse schema.
    
    Args:
        payload: The data to include in the response
        status_code: HTTP status code as a string
        request_id: Optional request ID to use instead of generating a new one
    
    Returns:
        Dict conforming to APIResponse structure
    """
    return APIResponse(payload, status_code, request_id).dict()


def create_pagination_response(
    content: List[T],
    total_elements: int,
    page: int,
    size: int,
    status_code: str = "200",
    request_id: Optional[str] = None
) -> dict[str, Any]:
    """Create a pagination response wrapped in APIResponse.

    Args:
        content: List of items for the current page
        total_elements: Total number of items across all pages
        page: Current page number (0-indexed)
        size: Number of items per page
        status_code: HTTP status code as a string
        request_id: Optional request ID to use instead of generating a new one

    Returns:
        Dict conforming to APIResponse structure with pagination data
    """
    total_pages = (total_elements + size - 1) // size
    pagination_data = APIResponsePagination(
        content=content,
        total_pages=total_pages,
        total_elements=total_elements,
        page=page,
        size=size,
        request_id=request_id
    ).dict()
    return create_response(pagination_data, status_code, request_id)