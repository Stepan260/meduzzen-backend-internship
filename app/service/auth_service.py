from datetime import datetime
from random import choices
from string import ascii_lowercase, digits

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
from app.utils.hash_password import verify_password, hash_password

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
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(decoded_token.get("exp"))
        if current_time >= expiration_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        user_email = decoded_token.get("email")

        user_repository = UserRepository(session=session)

        current_user = await user_repository.get_one(email=user_email)

        if not current_user:
            username_prefix = "UserName"
            random_suffix = ''.join(choices(ascii_lowercase + digits, k=10))
            username = username_prefix + random_suffix

            password = user_email.split('@')[0]
            hashed_password = hash_password(password)

            user_data = {
                "email": user_email,
                "username": username,
                "password": hashed_password
            }

            await user_repository.create_one(user_data)
            current_user = await user_repository.get_one(email=user_email)

        return current_user