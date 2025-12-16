from .base import AppException

class ExamPaperNotFoundError(AppException):
    status_code = 404
    message = "Đề thi không tồn tại"