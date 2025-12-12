from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.schemas.response import ResponseModel
from app.schemas.section import SectionCreate, SectionResponse, SectionUpdate
from app.services.exam_service import ExamService
from app.schemas.exam import ExamResponse, ExamCreate, ExamUpdate, ExamDetailResponse
from app.api.deps import get_exam_service, get_exam_paper_repository, get_section_repository, get_question_repository, \
    get_section_service
from app.services.section_service import SectionService


router = APIRouter()

# POST thêm section
@router.post("/{exam_paper_id}/sections", response_model=ResponseModel[SectionResponse], summary="Thêm mới section")
async def create_section(section_data:SectionCreate, exam_paper_id: str, section_service: SectionService = Depends(get_section_service),
                         user: dict = Depends(get_current_user)):
    new_section = await section_service.create_section(section_data, exam_paper_id)
    return ResponseModel(data=new_section, message="Thêm phần trong đề thành công")