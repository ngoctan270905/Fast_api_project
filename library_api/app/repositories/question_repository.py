from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionReadResponse


class QuestionRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("questions")


    # Truy vấn db lấy dữ liệu cho xem chi tiết đề thi ==================================================================
    async def get_by_section_ids(self, section_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"section_id": {"$in": section_ids}})
        questions = []
        async for question in cursor:
            questions.append(question)
        return questions


    # Truy vấn db thêm câu hỏi mới =====================================================================================
    async def create(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        insert_question = await self.collection.insert_one(question_data)
        question_data["_id"] = insert_question.inserted_id
        return question_data


    # Truy vấn db lấy thông tin question ===============================================================================
    async def get_by_id(self, question_id: str) -> Dict[str, Any]:
        question = await self.collection.find_one({"_id": ObjectId(question_id)})
        return question


    # Truy vấn db update question ======================================================================================
    async def update(self, question_id: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        updated_question = await self.collection.update_one({"_id": ObjectId(question_id)}, {"$set": question_data})
        new_question = await self.collection.find_one({"_id": ObjectId(question_id)})
        return new_question


    # Truy vấn db delete question ======================================================================================
    async def delete(self, question_id: str) -> bool:
        deleted = await self.collection.delete_one({"_id": ObjectId(question_id)})
        return deleted.deleted_count > 0


    # Truy vấn DB xóa nhiều question dựa trên ds section ===============================================================
    async def delete_many_by_section_ids(self, section_ids: List[ObjectId]) -> int:
        result = await self.collection.delete_many({"section_id": {"$in": section_ids}})
        return result.deleted_count

