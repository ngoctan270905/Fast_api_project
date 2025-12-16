from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client
from app.schemas.exam import ExamListResponse, ExamCreate
from app.schemas.question import QuestionResponse, QuestionCreate


class QuestionRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("questions")

    # Truy vấn db lấy dữ liệu cho xem chi tiết đề thi
    async def get_by_section_ids(self, section_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        # print(f"section_ids: {section_ids}")
        cursor = self.collection.find({"section_id": {"$in": section_ids}})
        questions = []
        async for question in cursor:
            questions.append(question)
        return questions

    # Truy vấn db thêm câu hỏi mới
    async def create(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        insert_question = await self.collection.insert_one(question_data)
        question_data["_id"] = insert_question.inserted_id
        return question_data

