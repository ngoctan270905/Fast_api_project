from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client
from app.schemas.exam import ExamListResponse, ExamCreate
from app.schemas.exam_paper import ExamPaperResponse


class ExamRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("exams")


    # Truy vấn db lấy ds bài kiểm tra ==================================================================================
    async def get_all_exam(self, grade: Optional[int] = None) -> List[Dict[str, Any]]:
        query = {}
        if grade is not None:
            query["grade"] = grade
        exams = []
        cursor = self.collection.find(query)
        async for exam in cursor:
            exams.append(exam)
        return exams


    # Truy vấn db thêm mới bài kiểm tra ================================================================================
    async def create(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        exam_data.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        insert_result = await self.collection.insert_one(exam_data)
        exam_data["_id"] = insert_result.inserted_id
        return exam_data


    #Truy vấn db sửa bài kiểm tra ======================================================================================
    async def update(self, exam_data: Dict[str, Any], exam_id:str) -> Dict[str, Any]:
        exam_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(exam_id)},
            {"$set": exam_data}
        )
        updated_exam = await self.collection.find_one({"_id": ObjectId(exam_id)})
        return updated_exam


    # Truy vấn db xem thông tin chi tiết exam ==========================================================================
    async def get_exam_by_id(self, exam_id: str) -> Dict[str, Any]:
        exam = await self.collection.find_one({"_id": ObjectId(exam_id)})
        print(f"tìm đc {exam}")
        return exam


    # Truy vấn db xóa bài kiểm tra kèm theo đề =========================================================================
    async def delete_one_by_id(self, exam_id: str) -> bool:
        deleted_exam = await self.collection.delete_one({"_id": ObjectId(exam_id)})
        return deleted_exam.deleted_count > 0

