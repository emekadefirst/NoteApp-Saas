from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utilities.crypto.jwt import JWTService
from src.errors.base import ErrorHandler


class AuthObjectMiddleware(BaseHTTPMiddleware):
    jwt = JWTService()
    error = ErrorHandler("Auth Middleware")

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        token = None

        # 🧩 Try to extract token from Authorization header first
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        # 🍪 If no header token, try cookies
        if not token:
            token = request.cookies.get("access_token")

        print(f"\n🔍 Authorization Header: {auth_header}")
        print(f"🍪 Cookie Token: {request.cookies.get('access_token')}")
        print(f"✅ Final Token Used: {token}")

        if not token:
            print("⚠️ No valid token found in headers or cookies\n")
            return await call_next(request)

        # Decode and attach user info
        payload = await self.jwt.decode_token(token)
        if not payload:
            print("❌ Invalid or expired token\n")
            return await call_next(request)

        # Example payload: {"id": "123", "user_type": "admin"}
        request.state.account = {"id": payload.get("id")}
        request.state.account_type = payload.get("user_type")

        print(f"✅ Authenticated as {payload.get('user_type')} with ID {payload.get('id')}\n")

        response = await call_next(request)
        return response
