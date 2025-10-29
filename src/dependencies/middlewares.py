from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.utilities.crypto.jwt import JWTService
from src.errors.base import ErrorHandler

class AuthObjectMiddleware(BaseHTTPMiddleware):
    jwt = JWTService()
    error = ErrorHandler("Auth Middleware")

    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        if not token:
            return await call_next(request)
        
        try:
            payload = await self.jwt.decode_token(token)
        except Exception:
            response = JSONResponse({"detail": "Login required"}, status_code=401)
            response.delete_cookie("access_token")
            return response

        if payload:
            request.state.user_id = payload.get("id")
            request.state.user_type = payload.get("user_type")
        return await call_next(request)
