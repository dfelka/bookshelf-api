class AppError(Exception):
    """Base class for domain errors mapped to the standard error envelope."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"
