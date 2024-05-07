import json
import statistics
from datetime import timedelta
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app.db.redisdb import redis_connection
from app.model.quizzes import Result
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.question_repository import QuestionRepository
from app.repository.result_repository import ResultRepository
from app.repository.users_repository import UserRepository
from app.schemas.question import QuestionUpdate, FullQuestionUpdate

from app.schemas.quizzes import (QuizCreate, UpdateQuiz, FullUpdateQuizResponse, QuizTake, QuizLastAttemptResponse,
                                 UserQuizAverageScoresResponse, UserLastAttemptResponse)

from app.service.сustom_exception import UserPermissionDenied, CompanyNotFound
from app.service.content_redis import redis_file_content
from app.utils.enum import CompanyRole
from app.utils.Analitics import calculate_user_average_scores_over_time, calculate_user_quiz_average_scores_over_time


class QuizService:
    def __init__(
            self,
            session: AsyncSession,
            quiz_repository: QuizRepository,
            question_repository: QuestionRepository,
            company_repository: CompanyRepository,
            action_repository: ActionRepository,
            user_repository: UserRepository,
            result_repository: ResultRepository
    ):
        self.quiz_repository = quiz_repository
        self.session = session
        self.question_repository = question_repository
        self.company_repository = company_repository
        self.action_repository = action_repository
        self.user_repository = user_repository
        self.result_repository = result_repository

    async def create_quiz(self, quiz_create: QuizCreate, user_uuid: UUID):
        company = await self.company_repository.get_one(uuid=quiz_create.company_uuid)
        user_role = await self.action_repository.get_one_by_params_or_404(
            company_uuid=quiz_create.company_uuid,
            user_uuid=user_uuid
        )

        if company.owner_uuid != user_uuid and user_role.role != CompanyRole.ADMIN:
            raise UserPermissionDenied()

        if len(quiz_create.questions) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz must contain at least two questions."
            )

        for question in quiz_create.questions:
            if len(question.answer_choices) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each question must have at least two answer choices."
                )

        quiz_without_question = quiz_create.model_dump(exclude={'questions'})
        quiz = await self.quiz_repository.create_one(quiz_without_question)
        questions = []
        for question_create in quiz_create.questions:
            question_data = question_create.model_dump()
            question_data['quiz_uuid'] = quiz.uuid
            question = await self.question_repository.create_one(question_data)
            questions.append(question)

        quiz.questions = questions

        return dict(
            message="Quiz created successfully.",
            quiz=quiz
        )

    async def quiz_update(self, quiz_uuid: UUID, quiz_update: UpdateQuiz, user_uuid: UUID) -> FullUpdateQuizResponse:
        quiz = await self.quiz_repository.get_one_by_params_or_404(uuid=quiz_uuid)

        user_role = await self.action_repository.get_one_by_params_or_404(company_uuid=quiz.company_uuid,
                                                                          user_uuid=user_uuid)

        if user_role.role not in [CompanyRole.ADMIN, CompanyRole.OWNER]:
            raise UserPermissionDenied()

        await self.quiz_repository.update_one(quiz_uuid, quiz_update.dict(exclude_unset=True))

        updated_quiz = await self.quiz_repository.get_one_by_params_or_404(uuid=quiz_uuid)

        update_quiz = UpdateQuiz(
            name=updated_quiz.name,
            description=updated_quiz.description,
            frequency_days=updated_quiz.frequency_days
        )

        return FullUpdateQuizResponse(
            message="Quiz updated successfully",
            quiz=update_quiz
        )

    async def question_update(self, question_uuid: UUID, update_question: QuestionUpdate,
                              ) -> FullQuestionUpdate:
        await self.question_repository.get_one_by_params_or_404(uuid=question_uuid)
        updated_question = await self.question_repository.update_one(question_uuid, update_question.model_dump())

        question_update_data = QuestionUpdate(
            text=updated_question.text,
            answer_choices=updated_question.answer_choices,
            correct_answer=updated_question.correct_answer
        )

        return FullQuestionUpdate(
            message="Question info updated successfully",
            question=question_update_data
        )

    async def delete_quiz(self, quiz_uuid: UUID, user_uuid: UUID) -> None:
        quiz = await self.quiz_repository.get_one_by_params_or_404(uuid=quiz_uuid)

        user_role = await self.action_repository.get_one_by_params_or_404(
            company_uuid=quiz.company_uuid,
            user_uuid=user_uuid
        )

        if user_role.role not in [CompanyRole.ADMIN, CompanyRole.OWNER]:
            raise UserPermissionDenied()

        await self.quiz_repository.delete_one(str(quiz_uuid))

    async def get_all_quizzes_by_company(self, skip: int = 1, limit: int = 10) -> dict:
        quizzes = await self.quiz_repository.get_many(skip=skip, limit=limit)
        return {'quizzes': quizzes}

    async def take_quiz(self, user_uuid: UUID, quiz_uuid: UUID, answers: QuizTake) -> Result:
        quiz = await self.quiz_repository.get_one_by_params_or_404(uuid=quiz_uuid)
        company = await self.company_repository.get_one_by_params_or_404(uuid=quiz.company_uuid)
        questions = await self.question_repository.get_many(skip=1, limit=100, quiz_uuid=quiz_uuid)

        quiz_result, correct_answers, total_questions = await self.process_answers(user_uuid, quiz, questions, answers)

        score, rounded_score = self.calculate_score(correct_answers, total_questions)

        await self._save_to_redis(user_uuid, company, quiz_uuid, quiz_result)

        return await self.create_result_entry(user_uuid, quiz_uuid, company, rounded_score, total_questions,
                                              correct_answers)

    async def process_answers(self, user_uuid: UUID, quiz, questions, answers: QuizTake):
        correct_answers = 0
        total_questions = len(questions)
        quiz_result = {
            'user_uuid': str(user_uuid),
            'company_uuid': str(quiz.company_uuid),
            'quiz_uuid': str(quiz.uuid),
            'questions': []
        }

        for question in questions:
            user_answer = answers.answers.get(question.uuid)
            is_correct = user_answer == question.correct_answer

            quiz_result['questions'].append({
                'question_uuid': str(question.uuid),
                'user_answer': user_answer,
                'is_correct': is_correct,
            })

            if is_correct:
                correct_answers += 1

        return quiz_result, correct_answers, total_questions

    def calculate_score(self, correct_answers, total_questions):
        score = (correct_answers / total_questions) * 100
        rounded_score = int(round(score, 2))
        return score, rounded_score

    async def _save_to_redis(self, user_uuid: UUID, company, quiz_uuid, quiz_result):
        redis_key = f"user:{user_uuid}:company:{company.uuid}:quiz:{quiz_uuid}:question:"
        redis_value = json.dumps(quiz_result)
        await redis_connection.set(redis_key, redis_value)
        await redis_connection.expire(redis_key, timedelta(hours=48))

    async def create_result_entry(self, user_uuid: UUID, quiz_uuid: UUID, company, rounded_score, total_questions,
                                  correct_answers):
        result = dict(
            user_uuid=user_uuid,
            quiz_uuid=quiz_uuid,
            company_uuid=company.uuid,
            score=rounded_score,
            total_questions=total_questions,
            correct_answers=correct_answers,
        )

        return await self.result_repository.create_one(result)

    async def get_user_quiz_results(self, user_uuid: UUID, file_format: str) -> FileResponse:
        query = f"user:{user_uuid}:company:*:quiz:*:question:"
        return await redis_file_content(query=query, file_format=file_format)

    async def get_company_quiz_answers_list(self, company_uuid: UUID, file_format: str,
                                            user_uuid: UUID) -> FileResponse:

        query = f"user:{user_uuid}:company:{company_uuid}:quiz:*:*question:"
        return await redis_file_content(query=query, file_format=file_format)

    async def get_company_quiz_answers_list(self, company_uuid: UUID, file_format: str) -> FileResponse:
        query = f"user:*:company:{company_uuid}:quiz:*:*question:"
        return await redis_file_content(query=query, file_format=file_format)

    async def get_user_rating(self, user_uuid: UUID) -> float:

        results = await self.result_repository.get_many(user_uuid=user_uuid, skip=1, limit=1000)

        if not results:
            return 0.0

        scores = [result.score for result in results]

        average_rating = statistics.mean(scores)

        return average_rating

    async def get_quizzes_average_scores(self) -> List[Dict]:

        results = await self.result_repository.get_many(skip=1, limit=1000)

        quiz_average_scores = {}

        for result in results:
            quiz_uuid = result.quiz_uuid
            score = result.score
            created_at = result.created_at

            if quiz_uuid not in quiz_average_scores:
                quiz_average_scores[quiz_uuid] = {
                    "quiz_uuid": quiz_uuid,
                    "average_scores": []
                }

            quiz_average_scores[quiz_uuid]["average_scores"].append({
                "score": score,
                "created_at": created_at
            })

        return list(quiz_average_scores.values())

    async def get_company_quizzes_last_attempts(self, company_uuid: UUID, user_uuid: UUID) -> List[
        QuizLastAttemptResponse]:

        user_role = await self.action_repository.get_one_by_params_or_404(
            company_uuid=company_uuid,
            user_uuid=user_uuid
        )
        if user_role.role not in [CompanyRole.ADMIN, CompanyRole.OWNER]:
            raise UserPermissionDenied()

        last_attempts_dict = {}

        results = await self.result_repository.get_many(
            skip=1,
            limit=1000,
            company_uuid=company_uuid
        )

        for result in results:
            quiz_uuid = result.quiz_uuid
            last_attempt_time = result.created_at

            if quiz_uuid not in last_attempts_dict:
                quiz = await self.quiz_repository.get_one_by_params_or_404(uuid=quiz_uuid)
                last_attempts_dict[quiz_uuid] = {
                    "quiz_uuid": quiz.uuid,
                    "quiz_name": quiz.name,
                    "last_attempt_time": last_attempt_time
                }

        return [QuizLastAttemptResponse(**data) for data in last_attempts_dict.values()]

    async def get_users_average_scores_over_time(self) -> List[Dict]:
        return await calculate_user_average_scores_over_time(self.result_repository)

    async def get_user_quiz_average_scores_over_time(self, user_uuid: UUID) -> List[UserQuizAverageScoresResponse]:
        return await calculate_user_quiz_average_scores_over_time(self.result_repository, user_uuid)

    async def get_company_users_last_attempts(
            self, company_uuid: UUID
    ) -> List[UserLastAttemptResponse]:

        results = await self.result_repository.get_many(
            company_uuid=company_uuid, skip=1, limit=1000
        )

        if not company_uuid:
            raise CompanyNotFound(identifier='uuid')

        user_last_attempts = {}

        for result in results:
            user_uuid = result.user_uuid
            created_at = result.created_at

            if user_uuid not in user_last_attempts or created_at > user_last_attempts[user_uuid]:
                user_last_attempts[user_uuid] = created_at

        user_last_attempts_list = [
            UserLastAttemptResponse(user_uuid=user_uuid, last_attempt_time=last_attempt_time)
            for user_uuid, last_attempt_time in user_last_attempts.items()
        ]

        return user_last_attempts_list
