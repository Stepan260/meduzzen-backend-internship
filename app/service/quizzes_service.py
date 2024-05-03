from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.question_repository import QuestionRepository
from app.schemas.question import QuestionUpdate, FullQuestionUpdate

from app.schemas.quizzes import QuizCreate, UpdateQuiz, FullUpdateQuizResponse
from app.service.сustom_exception import UserPermissionDenied, InsufficientQuizQuestions, InsufficientAnswerChoices
from app.utils.enum import CompanyRole


class QuizService:
    def __init__(
            self,
            session: AsyncSession,
            quiz_repository: QuizRepository,
            question_repository: QuestionRepository,
            company_repository: CompanyRepository,
            action_repository: ActionRepository
    ):
        self.quiz_repository = quiz_repository
        self.session = session
        self.question_repository = question_repository
        self.company_repository = company_repository
        self.action_repository = action_repository

    async def create_quiz(self, quiz_create: QuizCreate, user_uuid: UUID):
        company = await self.company_repository.get_one(uuid=quiz_create.company_uuid)
        user_role = await self.action_repository.get_one_by_params_or_404(
            company_uuid=quiz_create.company_uuid,
            user_uuid=user_uuid
        )

        if company.owner_uuid != user_uuid and user_role.role != CompanyRole.ADMIN:
            raise UserPermissionDenied()

        if len(quiz_create.questions) < 2:
            raise InsufficientQuizQuestions()

        for question in quiz_create.questions:
            if len(question.answer_choices) < 2:
                raise InsufficientAnswerChoices()

        quiz_without_question = quiz_create.model_dump(exclude={'questions'})
        quiz = await self.quiz_repository.create_one(quiz_without_question)
        questions = []
        for question_create in quiz_create.questions:
            question_data = question_create.model_dump()
            question_data['quiz_uuid'] = quiz.uuid
            question = await self.question_repository.create_one(question_data)
            questions.append(question)

        quiz.questions = questions

        return {"message": "create successful", "quiz": quiz}

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

        await self.quiz_repository.delete_one(quiz_uuid)

    async def get_all_quizzes_by_company(self, skip: int = 1, limit: int = 10) -> dict:
        quizzes = await self.quiz_repository.get_many(skip=skip, limit=limit)
        return {'quizzes': quizzes}
