from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
from app.exceptions.exam_paper_exception import ExamPaperNotFoundError
from app.exceptions.section_exception import SectionNotFoundError
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.repositories.section_repository import SectionRepository
from app.schemas.section import SectionCreate, SectionUpdate, SectionCreateResponse, SectionDetailResponse, SectionUpdateResponse


class SectionService:
    def __init__(self, section_repo: SectionRepository, exam_paper_repo: ExamPaperRepository):
        self.section_repo = section_repo
        self.exam_paper_repo = exam_paper_repo


    # Logic create section ======================================================================================
    async def create_section(self, section_create: SectionCreate, exam_paper_id: str) -> Optional[SectionCreateResponse]:
        exam_paper = await self.exam_paper_repo.get_by_id(exam_paper_id=exam_paper_id)
        if not exam_paper:
            raise ExamPaperNotFoundError()

        section_count = await self.section_repo.count_by_exam_paper(exam_paper_id)

        new_section_data = {
            "exam_paper_id": ObjectId(exam_paper_id),
            "title": section_create.title,
            "order": section_count + 1
        }

        new_section = await self.section_repo.create(new_section_data)
        return SectionCreateResponse(**new_section)


    # Logic read section ===============================================================================================
    async def get_by_section_id(self, section_id: str) -> Optional[SectionDetailResponse]:
        section = await self.section_repo.get_by_id(section_id=section_id)

        if not section:
            raise SectionNotFoundError()

        return SectionDetailResponse(**section)



    # Logic update section =============================================================================================
    async def update_section(self, section_id: str, section_update: SectionUpdate) -> Optional[SectionUpdateResponse]:
        section = await self.section_repo.get_by_id(section_id)

        if not section:
            raise SectionNotFoundError()

        update_data = section_update.model_dump(exclude_unset=True)
        updated = await self.section_repo.update(section_id, update_data)

        return SectionUpdateResponse(**updated)



    # Logic delete section =============================================================================================
    async def delete_section(self, section_id: str) -> bool:
        section = self.section_repo.get_by_id(section_id)
        deleted = await self.section_repo.delete(section_id)
        return deleted





