from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.section_repository import SectionRepository
from app.schemas.exam import ExamCreate, ExamUpdate, ExamListResponse, ExamDetailResponse
from app.schemas.section import SectionCreate, SectionResponse, SectionUpdate


class SectionService:
    def __init__(self, section_repo: SectionRepository, exam_paper_repo: ExamPaperRepository):
        self.section_repo = section_repo
        self.exam_paper_repo = exam_paper_repo

    async def create_section(self, section_create: SectionCreate, exam_paper_id: str) -> Optional[SectionResponse]:
        section_count = await self.section_repo.count_by_exam_paper(exam_paper_id)
        new_section_data = {
            "exam_paper_id": ObjectId(exam_paper_id),
            "title": section_create.title,
            "order": section_count + 1
        }

        new_section = await self.section_repo.create(new_section_data)
        return SectionResponse(**new_section)

    async def update_section(self, section_id: str, section_update: SectionUpdate) -> Optional[SectionResponse]:
        section = self.section_repo.get_by_section_id(section_id)

        update_data = section_update.model_dump(exclude_unset=True)
        updated = await self.section_repo.update(section_id, update_data)
        return SectionResponse(**updated)

    async def delete_section(self, section_id: str) -> bool:
        section = self.section_repo.get_by_section_id(section_id)

        deleted = await self.section_repo.delete(section_id)
        return deleted





