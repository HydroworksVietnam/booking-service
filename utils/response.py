from typing import Generic, TypeVar, Any, List
import uuid

T = TypeVar('T')

class APIResponse(Generic[T]):
    def __init__(self, payload: T, status_code: str = "200"):
        self.status = {
            "code": status_code
        }
        self.payload = payload
        self.meta = {
            "requestId": str(uuid.uuid4())
        }

    def dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "payload": self.payload,
            "meta": self.meta
        }


class APIResponsePagination(Generic[T]):
    def __init__(self, content: List[T], total_pages: int, total_elements: int, page: int, size: int):
        self.content = content
        self.totalPages = total_pages
        self.totalElements = total_elements
        self.page = page
        self.size = size

    def dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "totalPages": self.totalPages,
            "totalElements": self.totalElements,
            "page": self.page,
            "size": self.size
        }


def create_response(payload: T, status_code: str = "200") -> dict[str, Any]:
    """Create a response following the APIResponse schema."""
    return APIResponse(payload, status_code).dict()


def create_pagination_response(
    content: List[T],
    total_elements: int,
    page: int,
    size: int,
    status_code: str = "200"
) -> dict[str, Any]:
    """Create a pagination response wrapped in APIResponse.

    Args:
        content: List of items for the current page
        total_elements: Total number of items across all pages
        page: Current page number (0-indexed)
        size: Number of items per page
        status_code: HTTP status code as a string

    Returns:
        Dict conforming to APIResponse structure with pagination data
    """
    total_pages = (total_elements + size - 1) // size
    pagination_data = APIResponsePagination(
        content=content,
        total_pages=total_pages,
        total_elements=total_elements,
        page=page,
        size=size
    ).dict()
    return create_response(pagination_data, status_code)