from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client
from app.schemas.exam_paper import ExamPaperBase, ExamPaperDetail


class ExamPaperRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("exam_papers")

    # truy vấn db thêm đề thi
    async def create_many(self, papers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"testkkk{papers_data}")
        for paper in papers_data:
            paper["created_at"] = datetime.utcnow()
            paper["updated_at"] = datetime.utcnow()

        insert_result = await self.collection.insert_many(papers_data)
        inserted_ids = insert_result.inserted_ids

        inserted_docs = []
        async for doc in self.collection.find({"_id": {"$in": inserted_ids}}):
            inserted_docs.append(doc)
        return inserted_docs

    # Truy vấn db xem chi tiết
    async def get_by_exam_id(self, exam_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"exam_id": ObjectId(exam_id)}).sort("paper_number", 1)
        # print(f"Testkkk{cursor}")
        papers = []
        async for paper in cursor:
            papers.append(paper)
        print(f"tìm đc {len(papers)} đề thj")
        return papers
