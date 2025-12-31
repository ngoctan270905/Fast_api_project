from .base import AppException

class ExamNotFoundError(AppException):
    status_code = 404
    message = "Bài kiểm tra không tồn tại"


class NoFieldsToUpdateError(AppException):
    status_code = 400
    message = "Không có dữ liệu cần cập nhật"
