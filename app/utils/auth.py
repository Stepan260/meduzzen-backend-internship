from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException

from app.сore.config import settings


def create_jwt_token(email: str) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {"email": email, "exp": expiration, "aud": settings.AUDIENCE, "sub": 'noauth'}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms='HS256', audience=settings.AUDIENCE)
        if payload:
            return payload
        else:
            raise HTTPException(status_code=401, detail="Token is empty")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
