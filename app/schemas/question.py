from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class QuestionCreate(BaseModel):
    text: str
    answer_choices: List[str]
    correct_answer: str


class QuestionResponse(BaseModel):
    uuid: UUID
    text: str
    answer_choices: List[str]
    correct_answer: str


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    answer_choices: Optional[List[str]] = None
    correct_answer: Optional[str] = None


class FullQuestionUpdate(BaseModel):
    message: str
    question: QuestionUpdate
