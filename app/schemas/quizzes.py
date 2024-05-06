from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.schemas.question import QuestionCreate, QuestionResponse


class QuizCreate(BaseModel):
    name: str
    description: str
    frequency_days: int
    company_uuid: UUID
    questions: List[QuestionCreate]


class QuizResponse(BaseModel):
    name: str
    description: str
    frequency_days: int
    company_uuid: UUID
    questions: List[QuestionResponse]


class QuizzesResponse(BaseModel):
    name: str
    description: str
    frequency_days: int
    company_uuid: UUID


class FullQuizResponse(BaseModel):
    message: str
    quiz: QuizResponse


class UpdateQuiz(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency_days: Optional[int] = None


class FullUpdateQuizResponse(BaseModel):
    message: str
    quiz: UpdateQuiz


class QizzesListResponse(BaseModel):
    quizzes: List[QuizzesResponse]
