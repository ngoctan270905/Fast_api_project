from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any

from app.exceptions.question_exception import QuestionNotFoundError
from app.exceptions.section_exception import SectionNotFoundError
from app.repositories.question_repository import QuestionRepository
from app.repositories.section_repository import SectionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionCreateResponse, \
    QuestionReadResponse, QuestionUpdateResponse


class QuestionService:

    def __init__(self, question_repo: QuestionRepository, section_repo: SectionRepository):
        self.question_repo = question_repo
        self.section_repo = section_repo


    # Logic create question ============================================================================================
    async def create_question(self, question_data: QuestionCreate, section_id: str) -> QuestionCreateResponse:
        section = await self.section_repo.get_by_id(section_id)
        if not section:
            raise SectionNotFoundError()

        question_dict = question_data.model_dump()
        question_dict["section_id"] = ObjectId(section_id)
        question_dict["created_at"] = datetime.utcnow()
        question_dict["updated_at"] = datetime.utcnow()

        new_question = await self.question_repo.create(question_dict)
        return QuestionCreateResponse(**new_question)


    # Logic read question ==============================================================================================
    async def get_by_question(self, question_id: str) -> QuestionReadResponse:
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise QuestionNotFoundError()

        return QuestionReadResponse(**question)


    # Logic update question ============================================================================================
    async def update_question(self, question_id: str, question_data: QuestionUpdate) -> QuestionUpdateResponse:
        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise QuestionNotFoundError()

        question_dict = question_data.model_dump(exclude_unset=True)
        updated_question = await self.question_repo.update(question_id, question_dict)

        return QuestionUpdateResponse(**updated_question)


    # Logic delete question ============================================================================================
    async def delete_question(self, question_id: str) -> bool:
        print(f"Đi vào đây {question_id}")
        question = await self.question_repo.get_by_id(question_id)
        print(f"Tìm đc {question}")
        if not question:
            raise QuestionNotFoundError()

        deleted = await self.question_repo.delete(question_id)
        return deleted


