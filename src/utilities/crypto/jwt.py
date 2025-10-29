import jwt
from argon2 import PasswordHasher
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, Request, HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError, decode
from typing import Dict, Union
from src.errors.base import ErrorHandler
from src.configs.env import (
    JWT_ACCESS_EXPIRY,
    JWT_REFRESH_EXPIRY,
    JWT_ACCESS_SECRET,
    JWT_ALGORITHM,
)

error = ErrorHandler("Module")


class JWTService:
    @staticmethod
    def generate_token(payload: Dict[str, Union[str, dict]]) -> dict:
        """
        Accepts a payload like {"id": "...", "account_type": "admin"}
        and embeds it into both access and refresh tokens.
        """
        now = datetime.now(timezone.utc)

        access_exp = now + timedelta(minutes=JWT_ACCESS_EXPIRY)
        refresh_exp = now + timedelta(days=JWT_REFRESH_EXPIRY)

        # ✅ move your payload under "data" and keep "sub" a string
        access_payload = {
            "sub": "access",
            "data": payload,
            "exp": access_exp,
            "type": "access",
        }

        refresh_payload = {
            "sub": "refresh",
            "data": payload,
            "exp": refresh_exp,
            "type": "refresh",
        }

        access_token = jwt.encode(access_payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, JWT_ACCESS_SECRET, algorithm=JWT_ALGORITHM)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    async def decode_token(token: str):
        try:
            payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=[JWT_ALGORITHM])
            data = payload.get("data")

            # ✅ Fix: match your actual key "user_type"
            if not data or "id" not in data or "user_type" not in data:
                raise HTTPException(status_code=401, detail="Invalid token data")

            return data  # returns {"id": "...", "user_type": "admin"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            print(f"JWT Decode Error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_subject(token: str):
        payload = JWTService.decode_token(token)
        return payload.get("sub")

    @staticmethod
    async def get_current_user(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ):
        """
        Extracts and decodes JWT from cookies or Authorization header.
        Returns the user data dict (id and user_type).
        """
        access_token = request.cookies.get("access_token")

        # If no cookie, check Authorization header
        if not access_token and token and token.credentials:
            access_token = token.credentials

        if not access_token:
            raise HTTPException(status_code=401, detail="Missing access token")

        try:
            payload = await JWTService.decode_token(access_token)
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid access token")

        # ✅ payload = {"id": "...", "user_type": "admin"}
        if not payload.get("id"):
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return payload  # ✅ return dict, not just ID

    @staticmethod
    def refresh_token(refresh_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),):
        """
        Validates refresh token and issues a new pair of tokens.
        """
        payload = JWTService.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise error.get(400,"Invalid token type")
        user_id = payload.get("sub") 
        return JWTService.generate_token(user_id)

    @staticmethod
    def get_subject(token: str) -> str:
        payload = JWTService.decode_token(token)
        if not payload:
            raise error.unauthorized("Invalid or expired token")
        return payload.get("sub")
    
        

    # @staticmethod
    # async def get_current_user(
    #     request: Request,
    #     token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    # ):
    #     credentials_exception = HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Could not validate credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    #     access_token = request.cookies.get("access_token")

    #     if not access_token and token and token.credentials:
    #         access_token = token.credentials

    #     if not access_token:
    #         raise credentials_exception

    #     try:
    #         payload = JWTService.decode_token(access_token)
    #     except ExpiredSignatureError:
    #         raise HTTPException(status_code=401, detail="Access token expired")
    #     except InvalidTokenError:
    #         raise HTTPException(status_code=401, detail="Invalid access token")

    #     sub = payload.get("sub")
    #     if not sub:
    #         raise credentials_exception

    #     return sub.get("id") if isinstance(sub, dict) else sub


