from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client
from app.schemas.exam import ExamResponse, ExamCreate
from app.schemas.question import QuestionResponse

class QuestionRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("questions")

    # Truy vấn db lấy dữ liệu
    async def get_by_section_ids(self, section_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        # print(f"section_ids: {section_ids}")
        cursor = self.collection.find({"section_id": {"$in": section_ids}})
        questions = []
        async for question in cursor:
            questions.append(question)
        return questions