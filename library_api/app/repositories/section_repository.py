from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.core.mongo_database import mongodb_client


class SectionRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("sections")

    # Truy vấn db để thêm section ======================================================================================
    async def create(self, section_create: Dict[str, Any]) -> Dict[str, Any]:
        insert_section = await self.collection.insert_one(section_create)
        section_create["_id"] = insert_section.inserted_id
        return section_create


    # Truy vấn db để sửa section =======================================================================================
    async def update(self, section_id: str, section_update: dict) -> Dict[str, Any]:
        section_update["updated_at"] = datetime.utcnow()
        update_section = await self.collection.update_one(
            {"_id": ObjectId(section_id)},
            {"$set": section_update}
        )
        ket_qua = await self.collection.find_one({"_id": ObjectId(section_id)})
        return ket_qua


    # Truy vấn db để đọc section =======================================================================================
    async def get_by_id(self, section_id: str) -> Dict[str, Any]:
        section = await self.collection.find_one({"_id": ObjectId(section_id)})
        return section


    # Truy vấn db lấy ds sections trong exam_paper =====================================================================
    async def get_by_paper_ids(self, paper_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        print(f"paper ids {paper_ids}")
        cursor = self.collection.find({"exam_paper_id": {"$in": paper_ids}})
        sections = []
        async for section in cursor:
            sections.append(section)
        return sections


    # Truy vấn db tính số section hiện có của đề thi ===================================================================
    async def count_by_exam_paper(self, exam_paper_id: str) -> int:
        count = await self.collection.count_documents({"exam_paper_id": ObjectId(exam_paper_id)})
        return count


    # Truy vấn db để xóa section =======================================================================================
    async def delete(self, section_id: str) -> bool:
        delete_section = await self.collection.delete_one({"_id": ObjectId(section_id)})
        return delete_section.deleted_count > 0


    # Truy vấn db để xóa nhiều section dựa trên exam_paper_id ==========================================================
    async def delete_many_by_paper_ids(self, paper_ids: List[ObjectId]) -> int:
        result = await self.collection.delete_many({"exam_paper_id": {"$in": paper_ids}})
        return result.deleted_count


