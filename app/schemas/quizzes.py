from datetime import datetime, date

from pydantic import BaseModel
from typing import List, Optional, Dict
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


class QuizTake(BaseModel):
    answers: Dict[UUID, Optional[str]]


class TestResultCreateSchema(BaseModel):
    user_uuid: UUID
    quiz_uuid: UUID
    company_uuid: UUID
    correct_answers: int
    total_questions: int
    score: int


class SendFile(BaseModel):
    file: bytes
    filename: str


class AverageScoreWithDate(BaseModel):
    score: float
    created_at: datetime


class QuizAverageScoresResponse(BaseModel):
    quiz_uuid: UUID
    average_scores: List[AverageScoreWithDate]


class QuizLastAttemptResponse(BaseModel):
    quiz_uuid: UUID
    quiz_name: str
    last_attempt_time: datetime


class UserAverageScoresResponse(BaseModel):
    user_uuid: UUID
    date_period: date
    average_score: float


class UserQuizAverageScoresResponse(BaseModel):
    quiz_uuid: UUID
    date_period: date
    average_score: float


class UserLastAttemptResponse(BaseModel):
    user_uuid: UUID
    last_attempt_time: datetime
