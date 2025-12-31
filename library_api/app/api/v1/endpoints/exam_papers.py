from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.schemas.response import ResponseModel
from app.schemas.section import SectionCreate, SectionUpdate
from app.services.exam_service import ExamService
from app.schemas.exam import ExamListResponse, ExamCreate, ExamUpdate, ExamDetailResponse
from app.api.deps import get_exam_service, get_exam_paper_repository, get_section_repository, get_question_repository, \
    get_section_service
from app.services.section_service import SectionService


router = APIRouter()

