class VoxylAPIError(Exception):
    """Base exception for all Voxyl API wrapper errors."""
    pass


class VoxylRateLimitError(VoxylAPIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""
    def __init__(self, message: str = "Rate limit exceeded. Please wait before retrying."):
        super().__init__(message)


class VoxylClientError(VoxylAPIError):
    """Raised for client-side issues (e.g., network errors)."""
    def __init__(self, message: str = "Client error occurred during request."):
        super().__init__(message)


class VoxylUnexpectedStatusError(VoxylAPIError):
    """Raised when the API returns an unexpected HTTP status code."""
    def __init__(self, status_code: int, message: str | None = None):
        msg = message or f"Unexpected status code: {status_code}"
        super().__init__(msg)
        self.status_code = status_code


class VoxylInvalidRequestError(VoxylAPIError):
    """Raised for invalid parameters or malformed requests (HTTP 400)."""
    def __init__(self, message: str = "Invalid request. Please check the parameters."):
        super().__init__(message)


class VoxylNotFoundError(VoxylAPIError):
    """Raised when the requested resource was not found (HTTP 404)."""
    def __init__(self, resource: str = "resource"):
        super().__init__(f"{resource.capitalize()} not found.")