from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import bcrypt

from app.db.postgres import get_session
from app.repository.users_repository import UserRepository
from app.schemas.auth import SignUpRequest, SignInRequest, AccessToken
from app.schemas.user import UserDetail
from app.service.сustom_exception import UserAlreadyExist, UserNotFound
from app.utils.auth import create_jwt_token, verify_jwt_token
from app.utils.hash_password import verify_password

security = HTTPBearer()


class AuthService:
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self.session = session
        self.repository = repository

    async def signup(self, user_create: SignUpRequest):
        email = user_create.email
        password = user_create.password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db_user = await self.repository.get_one(email=email)
        if db_user:
            raise UserAlreadyExist(identifier=email)

        user_with_hashed_password = user_create.copy(update={"password": hashed_password})

        await self.repository.create_one(user_with_hashed_password.dict())

        token = create_jwt_token(email=email)

        return {"access_token": token, "token_type": "bearer"}

    async def login(self, data: SignInRequest) -> AccessToken:
        email = data.email
        password = data.password

        user = await self.repository.get_one(email=email)
        if not user:
            raise UserNotFound(identifier=email)

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = create_jwt_token(email=email)

        return {"access_token": token, "token_type": "bearer"}

    @staticmethod
    async def get_current_user(
            token: HTTPAuthorizationCredentials = Depends(security),
            session: AsyncSession = Depends(get_session)
    ) -> UserDetail:
        decoded_token = verify_jwt_token(token.credentials)
        user_repository = UserRepository(session=session)
        db_user = await user_repository.get_one(email=decoded_token.get('email'))
        if not db_user:
            raise UserNotFound(identifier=decoded_token.get('email'))
        return db_user
