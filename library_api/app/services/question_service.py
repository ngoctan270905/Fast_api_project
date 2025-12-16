from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.section_repository import SectionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse


class QuestionService:

    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    async def create_question(self, question_data: QuestionCreate, section_id: str) -> QuestionResponse:
        question_dict = question_data.model_dump()
        question_dict["section_id"] = ObjectId(section_id)
        new_question = await self.question_repo.create(question_dict)
        return QuestionResponse(**new_question)