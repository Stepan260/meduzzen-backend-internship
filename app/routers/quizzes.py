from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.users_repository import UserRepository
from app.repository.action_repository import ActionRepository
from app.repository.company_repository import CompanyRepository
from app.repository.question_repository import QuestionRepository
from app.repository.quizzes_repository import QuizRepository
from app.repository.result_repository import ResultRepository
from app.schemas.question import QuestionUpdate, FullQuestionUpdate
from app.schemas.quizzes import QuizCreate, FullQuizResponse, UpdateQuiz, FullUpdateQuizResponse, \
    QizzesListResponse, QuizTake, TestResultCreateSchema, SendFile
from app.schemas.user import UserDetail
from app.service.auth_service import AuthService
from app.service.quizzes_service import QuizService
from app.db.postgres import get_session


async def get_quizzes_service(session: AsyncSession = Depends(get_session)) -> QuizService:
    quiz_repository = QuizRepository(session)
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    question_repository = QuestionRepository(session)
    user_repository = UserRepository(session)
    result_repository = ResultRepository(session)

    return QuizService(
        session=session,
        quiz_repository=quiz_repository,
        action_repository=action_repository,
        company_repository=company_repository,
        question_repository=question_repository,
        user_repository=user_repository,
        result_repository=result_repository
    )


router = APIRouter(tags=["Quizzes"])


@router.post("/create", response_model=FullQuizResponse)
async def create_quiz(
        quiz_create: QuizCreate,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await quiz_service.create_quiz(quiz_create, current_user.uuid)


@router.put("/{quiz_uuid}/update_info", response_model=FullUpdateQuizResponse)
async def edit_quiz(
        quiz_uuid: UUID,
        quiz_update: UpdateQuiz,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await quiz_service.quiz_update(quiz_uuid=quiz_uuid, quiz_update=quiz_update, user_uuid=current_user.uuid)


@router.post("/{question_uuid}/update_info", response_model=FullQuestionUpdate)
async def question_update(
        question_uuid: UUID,
        update_question: QuestionUpdate,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await quiz_service.question_update(question_uuid=question_uuid, update_question=update_question)


@router.delete("/quizzes/{quiz_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
        quiz_uuid: UUID,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    await quiz_service.delete_quiz(quiz_uuid=quiz_uuid, user_uuid=current_user.uuid)
    return None


@router.get("/quizzes/", response_model=QizzesListResponse)
async def get_all_quizzes(
        company_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user),
        skip: int = 1, limit: int = 10):
    return await company_service.get_all_quizzes_by_company(skip=skip, limit=limit)


@router.post("/quizzes/{quiz_uuid}/take_quiz", response_model=TestResultCreateSchema)
async def take_quiz(
        quiz_uuid: UUID,
        answers: QuizTake,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    return await quiz_service.take_quiz(
        user_uuid=current_user.uuid,
        quiz_uuid=quiz_uuid,
        answers=answers,
    )


@router.get("/last_answers_list", response_model=SendFile)
async def user_last_answers_list_route(
        file_format: str,
        quiz_service: QuizService = Depends(get_quizzes_service),
        current_user: UserDetail = Depends(AuthService.get_current_user)
):
    current_user_uuid = current_user.uuid
    return await quiz_service.get_user_quiz_results(user_uuid=current_user_uuid, file_format=file_format)


@router.get("/{company_uuid}/last_answers_list/{user_uuid}", response_model=SendFile)
async def company_last_answers_list_route(company_uuid: UUID,
                                          file_format: str,
                                          user_uuid: UUID,
                                          quiz_service: QuizService = Depends(get_quizzes_service),
                                          current_user: UserDetail = Depends(AuthService.get_current_user)
                                          ):
    return await quiz_service.company_last_answers_list(company_uuid=company_uuid, user_uuid=user_uuid,
                                                        file_format=file_format)


@router.get("/{company_id}/last_answers_list", response_model=SendFile)
async def company_last_answers_list_route(company_uuid: UUID,
                                          file_format: str,
                                          session: AsyncSession = Depends(get_session),
                                          quiz_service: QuizService = Depends(get_quizzes_service),
                                          current_user: UserDetail = Depends(AuthService.get_current_user)
                                          ):
    return await quiz_service.company_last_answers_list(company_uuid=company_uuid, file_format=file_format)



