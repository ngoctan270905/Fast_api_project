from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId

from app.core.mongo_database import mongodb_client
from app.schemas.exam import ExamResponse, ExamCreate
from app.schemas.exam_paper import ExamPaperResponse


class ExamRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("exams")


    # Truy vấn db lấy ds bài kiểm tra
    async def get_all_exam(self) -> List[Dict[str, Any]]:
        exams = []
        cursor = self.collection.find({"deleted":None})
        async for exam in cursor:
            exams.append(exam)
        return exams


    # Truy vấn db thêm mới bài kiểm tra
    async def create(self, exam_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        exam_data.update({
            "created_by": ObjectId(user_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "deleted_at": None
        })
        insert_result = await self.collection.insert_one(exam_data)
        exam_data["_id"] = insert_result.inserted_id
        return exam_data


    # Truy vấn db xem thông tin chi tiết exam
    async def get_exam_by_id(self, exam_id: str) -> Dict[str, Any]:
        exam = await self.collection.find_one({"_id": ObjectId(exam_id), "deleted_at":None})
        print(f"tìm đc {exam}")
        return exam

