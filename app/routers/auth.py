from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import SignUpRequest, SignInRequest, AccessToken
from app.schemas.user import UserDetail
from app.service.auth_service import AuthService
from app.db.postgres import get_session
from app.repository.users_repository import UserRepository

router = APIRouter()


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(session=session, repository=user_repository)


@router.post("/signup", response_model=AccessToken, tags=["auth"])
async def signup_route(user_create: SignUpRequest,
                       user_service: AuthService = Depends(get_auth_service)):
    return await user_service.signup(user_create)


@router.post("/login", response_model=AccessToken, tags=["auth"])
async def login_route(data: SignInRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(data)


@router.get("/me", tags=["auth"], response_model=UserDetail)
async def get_current_user_route(current_user: UserDetail = Depends(AuthService.get_current_user)):
    return current_user
