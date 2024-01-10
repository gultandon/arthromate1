"""Typed error classes for the application."""


class AppError(Exception):
    """Base application error with HTTP status code and error code."""

    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class ValidationError(AppError):
    """Raised when request validation fails."""

    def __init__(self, message: str):
        super().__init__(message, 400, "VALIDATION_ERROR")


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, 404, "NOT_FOUND")


class UnauthorizedError(AppError):
    """Raised when authentication is missing or invalid."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")


class ConflictError(AppError):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str):
        super().__init__(message, 409, "CONFLICT")
