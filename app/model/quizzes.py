import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Column, String, ForeignKey, Integer, Text, DateTime


from app.model.base_models import BaseClass


class Quiz(BaseClass):
    __tablename__ = 'quizzes'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    frequency_days = Column(Integer, nullable=False)
    company_uuid = Column(UUID(as_uuid=True), ForeignKey('companies.uuid', ondelete='CASCADE'))


class Question(BaseClass):
    __tablename__ = 'questions'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_uuid = Column(UUID, ForeignKey('quizzes.uuid', ondelete='CASCADE'))
    text = Column(Text, nullable=False)
    answer_choices = Column(ARRAY(String), nullable=False)
    correct_answer = Column(String, nullable=False)


class Result(BaseClass):
    __tablename__ = "results"

    uuid = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_uuid = Column(UUID, ForeignKey("users.uuid"), nullable=False)
    company_uuid = Column(UUID, ForeignKey("companies.uuid"), nullable=False)
    quiz_uuid = Column(UUID, ForeignKey("quizzes.uuid"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
