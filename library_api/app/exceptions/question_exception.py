from .base import AppException

class QuestionNotFoundError(AppException):
    status_code = 404
    message = "Câu hỏi không tồn tại"