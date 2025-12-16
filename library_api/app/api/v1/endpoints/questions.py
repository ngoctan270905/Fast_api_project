from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.schemas.question import QuestionResponse, QuestionCreate
from app.schemas.response import ResponseModel
from app.api.deps import get_question_service
from app.services.question_service import QuestionService


router = APIRouter()

# POST thêm câu hỏi ====================================================================================================
@router.post("/section/{section_id}/questions", response_model=ResponseModel[QuestionResponse], summary="Thêm mới câu hỏi")
async def create_question(section_id:str, question_data: QuestionCreate,
                          question_service: QuestionService = Depends(get_question_service),):

    new_question = await question_service.create_question(question_data, section_id)
    return ResponseModel(data=new_question, message="Thêm câu hỏi thành công")


