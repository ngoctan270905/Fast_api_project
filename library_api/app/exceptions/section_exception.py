from .base import AppException

class SectionNotFoundError(AppException):
    status_code = 404
    message = "Section không tồn tại"