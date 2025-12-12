from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.section_repository import SectionRepository
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamDetailResponse

class ExamService:
    def __init__(self, exam_repo: ExamRepository, exam_paper_repo: ExamPaperRepository,
                 section_repo: SectionRepository, question_repo: QuestionRepository):
        self.exam_repo = exam_repo
        self.exam_paper_repo = exam_paper_repo
        self.section_repo = section_repo
        self.question_repo = question_repo


    # Logic lấy danh sách bài kiểm tra
    async def get_all_exams(self) -> List[ExamResponse]:
        exams_data = await self.exam_repo.get_all_exam()
        exams = []
        for exam in exams_data:
            exam_response = ExamResponse(**exam)
            exams.append(exam_response)
        return exams


    # Logic thêm bài kiểm tra kèm số đề thi
    async def create_exam(self, exam_create: ExamCreate, user_id:str) -> ExamResponse:
        exam_dict = exam_create.model_dump()
        exam_record = await self.exam_repo.create(exam_dict, user_id)
        exam_id = str(exam_record["_id"])  # Lấy ID sau insert

        exam_number = exam_create.exam_number
        # Tạo danh sách để lưu thông tin các đề thi
        papers_data: List[Dict[str, Any]] = []

        for paper_num in range(1, exam_number + 1):
            paper_data = {
                "exam_id": ObjectId(exam_id),
                "paper_number": paper_num,
                "title": f"Đề số {paper_num}"
            }
            papers_data.append(paper_data)

        if papers_data:
            await self.exam_paper_repo.create_many(papers_data)
        return ExamResponse(**exam_record)


    # Logic xem chi tiết bài kiểm tra
    async def get_exam_by_id(self, exam_id: str) -> Optional[Dict[str, Any]]:

        # -----------------------------------------------------
        # 1. Lấy thông tin bài kiểm tra theo id
        # -----------------------------------------------------
        exam = await self.exam_repo.get_exam_by_id(exam_id)
        if not exam:
            return None

        # -----------------------------------------------------
        # 2. Lấy danh sách đề thi
        # -----------------------------------------------------
        exam_papers = await self.exam_paper_repo.get_by_exam_id(exam_id)
        if not exam_papers:
            exam["exam_papers"] = []
            return exam
        exam["exam_papers"] = exam_papers

        # Lấy danh sách ID của từng đề
        exam_paper_ids = []
        for paper in exam_papers:
            exam_paper_ids.append(paper["_id"])
        # print(f"danh sách id để lấy section {exam_paper_ids}")

        # -----------------------------------------------------
        # 3. Lấy danh sách các section theo danh sách paper_ids
        # -----------------------------------------------------
        sections = await self.section_repo.get_by_paper_ids(exam_paper_ids)
        if not sections:
            for paper in exam_papers:
                paper["sections"] = []
            return exam

        # Lấy list section_id
        section_ids = []
        for section in sections:
            section_ids.append(section["_id"])
        # print(f"test {section_ids}")

        # -----------------------------------------------------
        # 4. Lấy danh sách câu hỏi theo section_ids
        # -----------------------------------------------------
        questions = await self.question_repo.get_by_section_ids(section_ids)
        # print(f"tìm đc số câu {len(questions)}")

        # Gom câu hỏi vào từng section
        questions_by_section = {}
        for question in questions:
            section_id = question["section_id"] # gán section_id = section_id

            if section_id not in questions_by_section:
                questions_by_section[section_id] = []

            questions_by_section[section_id].append(question) # thêm câu hỏi vào ds câu hỏi của section

        # -----------------------------------------------------
        # 5. Gom section vào từng exam_paper
        # -----------------------------------------------------
        sections_grouped_by_paper = {}

        for section in sections:
            section_id = section["_id"]
            exam_paper_id = section["exam_paper_id"]

            # Gắn danh sách câu hỏi vào section
            section["questions"] = questions_by_section.get(section_id, [])

            # Nếu paper này chưa có key → khởi tạo list
            if exam_paper_id not in sections_grouped_by_paper:
                sections_grouped_by_paper[exam_paper_id] = []

            # Thêm section vào đúng paper tương ứng
            sections_grouped_by_paper[exam_paper_id].append(section)

        # -----------------------------------------------------
        # 6. Gắn sections vào từng exam_paper
        # -----------------------------------------------------
        for exam_paper in exam_papers:
            exam_paper_id = exam_paper["_id"]

            exam_paper["sections"] = sections_grouped_by_paper.get(exam_paper_id, [])

        return exam

