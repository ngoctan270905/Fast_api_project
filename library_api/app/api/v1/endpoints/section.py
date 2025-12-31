from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.response import ResponseModel
from app.schemas.section import SectionCreate, SectionUpdate, SectionCreateResponse, \
    SectionDetailResponse, SectionUpdateResponse
from app.api.deps import get_section_service
from app.services.section_service import SectionService

router = APIRouter()

# POST thêm section ====================================================================================================
@router.post("/exam_paper/{exam_paper_id}/sections", response_model=ResponseModel[SectionCreateResponse], summary="Thêm mới section")
async def create_section(section_data:SectionCreate, exam_paper_id:str,
                         section_service: SectionService = Depends(get_section_service)):

    new_section = await section_service.create_section(section_data, exam_paper_id)
    return ResponseModel(data=new_section, message="Create section thành công")



# GET xem thông tin section ============================================================================================
@router.get("/sections/{section_id}", response_model=ResponseModel[SectionDetailResponse], summary="Xem thông tin section")
async def read_section(section_id:str, section_service: SectionService = Depends(get_section_service)):

    section = await section_service.get_by_section_id(section_id=section_id)
    return ResponseModel(data=section, message="Lấy thông tin section thành công")



# PUT sửa section ======================================================================================================
@router.put("/sections/{section_id}", response_model=ResponseModel[SectionUpdateResponse], summary="Chỉnh sửa section")
async def update_section(section_data:SectionUpdate,section_id:str,
                         section_service: SectionService = Depends(get_section_service)):

    updated = await section_service.update_section(section_id, section_data)
    return ResponseModel(data=updated, message="Sửa phần trong đề thành công")



# DELETE xóa section ===================================================================================================
@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa section")
async def update_section(section_id:str, section_service: SectionService = Depends(get_section_service)):

    deleted = await section_service.delete_section(section_id)
    return deleted


