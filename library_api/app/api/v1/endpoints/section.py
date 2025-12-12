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



# PUT sửa section
@router.put("/{section_id}", response_model=ResponseModel[SectionResponse], summary="Chỉnh sửa section")
async def update_section(section_data:SectionUpdate,section_id:str,
                         section_service: SectionService = Depends(get_section_service), user: dict = Depends(get_current_user)):
    updated = await section_service.update_section(section_id, section_data)
    return ResponseModel(data=updated, message="Sửa phần trong đề thành công")

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa section")
async def update_section(section_id:str,
                         section_service: SectionService = Depends(get_section_service), user: dict = Depends(get_current_user)):
    deleted = await section_service.delete_section(section_id)
    return deleted