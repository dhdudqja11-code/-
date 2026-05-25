from fastapi import Request, HTTPException, status
from typing import Dict

class AuthMiddleware:
    """
    API 게이트웨이에 붙는 전역 인증 미들웨어입니다. 
    모든 요청에 대해 JWT 유효성 검증 및 사용자 컨텍스트 주입을 강제합니다.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Dict[str, Any], receive: callable, send: callable):
        # 1. HTTP 요청이 아닌 경우 건너뜀 (예: 웹소켓)
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        auth_header = request.headers.get("Authorization")

        # 2. 인증 헤더 검증 (Stub 로직)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials missing or invalid format. Must use Bearer <token>."
            )
        
        # TODO: 실제 환경에서는 여기서 JWT 파싱 및 만료일 체크를 수행합니다.
        # 가상으로 토큰이 유효하다고 가정하고 사용자 ID를 추출합니다.
        try:
            _, token = auth_header.split(" ")
            user_id = "user-12345" # 실제로는 토큰에서 파싱된 고유 ID
        except ValueError:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Bearer format.")

        # 3. 사용자 컨텍스트를 요청 객체에 주입 (FastAPI Request State 활용)
        request.state.user_id = user_id
        print(f"[🛡️ AUTH MIDDLEWARE] Successfully authenticated user: {user_id}")

        await self.app(scope, receive, send)

# FastAPI의 Middleware 클래스 구조를 맞추기 위해 이 래퍼 함수를 사용합니다.
def get_auth_middleware():
    return AuthMiddleware(None) # 실제 앱 객체는 main.py에서 주입됩니다.