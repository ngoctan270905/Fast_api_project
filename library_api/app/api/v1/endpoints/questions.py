from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionCreateResponse, QuestionReadResponse, \
    QuestionUpdateResponse, QuestionUpdate
from app.schemas.response import ResponseModel
from app.api.deps import get_question_service
from app.services.question_service import QuestionService


router = APIRouter()

# POST thêm câu hỏi ====================================================================================================
@router.post("/section/{section_id}/questions", response_model=ResponseModel[QuestionCreateResponse], summary="Thêm mới câu hỏi")
async def create_question(section_id:str, question_data: QuestionCreate,
                          question_service: QuestionService = Depends(get_question_service),):

    new_question = await question_service.create_question(question_data, section_id)
    return ResponseModel(data=new_question, message="Thêm câu hỏi thành công")



# GET xem câu hỏi ======================================================================================================
@router.get("/questions/{question_id}", response_model=ResponseModel[QuestionReadResponse], summary="Xem chi tiết câu hỏi")
async def read_question(question_id:str, question_service: QuestionService = Depends(get_question_service)):

    question = await question_service.get_by_question(question_id)
    return ResponseModel(data=question, message="Lấy thông tin câu hỏi thành công")



# PUT update câu hỏi ===================================================================================================
@router.put("/questions/{question_id}", response_model=ResponseModel[QuestionUpdateResponse], summary="Cập nhật câu hỏi")
async def update_question(question_id:str, question_data: QuestionUpdate, question_service: QuestionService = Depends(get_question_service)):

    updated_question = await question_service.update_question(question_id, question_data)
    return ResponseModel(data=updated_question, message="Lấy thông tin câu hỏi thành công")



# DELETE question ======================================================================================================
@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa câu hỏi")
async def delete_question(question_id:str, question_service: QuestionService = Depends(get_question_service)):
    deleted = await question_service.delete_question(question_id)
    return deleted


