from datetime import datetime
from typing import Optional, List, Dict, Any

from bson import ObjectId

from app.core.mongo_database import mongodb_client
from app.schemas.exam import ExamResponse, ExamCreate
from app.schemas.section import SectionResponse, SectionDetail, SectionCreate, SectionUpdate


class SectionRepository:
    def __init__(self):
        self.db = mongodb_client.get_database()
        self.collection = self.db.get_collection("sections")

    # Truy vấn db để thêm section
    async def create(self, section_create: Dict[str, Any]) -> Dict[str, Any]:
        # section_data = section_create.model_dump()
        insert_section = await self.collection.insert_one(section_create)
        section_create["_id"] = insert_section.inserted_id
        return section_create

    # Truy vấn db để sửa section
    async def update(self, section_id: str, section_update: dict) -> Dict[str, Any]:
        update_section = await self.collection.update_one(
            {"_id": ObjectId(section_id)},
            {"$set": section_update}
        )
        ket_qua = await self.collection.find_one({"_id": ObjectId(section_id)})
        return ket_qua

    async def get_by_section_id(self, section_id: str) -> Dict[str, Any]:
        section = await self.collection.find_one({"_id": ObjectId(section_id)})
        return section


    # Truy vấn db lấy dữ liệu
    async def get_by_paper_ids(self, paper_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"exam_paper_id": {"$in": paper_ids}})
        sections = []
        async for section in cursor:
            sections.append(section)
        # print(f"Found {len(sections)} sections")
        return sections

    # Truy vấn db tính số section hiện có của đề thi
    async def count_by_exam_paper(self, exam_paper_id: str) -> int:
        # return await self.collection.count_documents({"exam_paper_id": exam_paper_id})
        count = await self.collection.count_documents({"exam_paper_id": ObjectId(exam_paper_id)})
        print(f"count {count}")
        return count

    # Truy vấn db để xóa section
    async def delete(self, section_id: str) -> bool:
        delete_section = await self.collection.delete_one({"_id": ObjectId(section_id)})
        return delete_section.deleted_count > 0


