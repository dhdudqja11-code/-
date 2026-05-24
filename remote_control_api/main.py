from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from services.authentication_service import AuthenticationService
from services.session_manager import SessionManager

# 💡 초기화 및 의존성 주입 설정
app = FastAPI(title="Remote Control API Gateway", version="0.1.0")

auth_service = AuthenticationService()
session_manager = SessionManager()

class Credentials(BaseModel):
    username: str
    password: str

class TokenPayload(BaseModel):
    user_id: str
    device_ip: str

# --- Dependency Functions (보안 게이트) ---

def get_current_user_info(token: str = Depends(lambda: "Bearer dummy_token")):
    """
    요청 헤더에서 토큰을 추출하고 유효성을 검사하는 의존성 함수.
    실제로는 HTTP Request 객체에서 Bearer token을 받아야 합니다.
    """
    user_id = auth_service.get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credentials.")
    
    # 🚨 보안 필수 체크: MFA 강제 확인 로직 추가
    if not auth_service.enforce_mfa_check(user_id, token):
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA required or failed.")

    return {"user_id": user_id}


# --- API Endpoints ---

@app.post("/auth/login")
def login_for_access_token(credentials: Credentials):
    """사용자 로그인 및 JWT Access Token 발급."""
    print("Attempting login...")
    # 1. 사용자 DB 조회 (가정)
    if not auth_service.verify_password(credentials.password, "dummy_hashed_pass"): # TODO: DB lookup
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    user_id = "USER_" + credentials.username 
    
    # 2. Access Token 생성 (30분 유효)
    access_token = auth_service.create_access_token(data={"sub": user_id}, expires_delta=timedelta(minutes=30))

    # 3. 세션 생성 및 등록
    session_manager.create_session(user_id, access_token, duration_minutes=60)
    
    return {"access_token": access_token, "token_type": "bearer", "expires_in": 1800}


@app.get("/api/v1/data/{resource_id}")
def get_protected_data(user_info: dict = Depends(get_current_user_info), resource_id: str):
    """
    🚨 보호된 엔드포인트 예시. 
    사용자 인증과 세션 유효성 검증이 성공해야만 접근 가능합니다.
    """
    user_id = user_info['user_id']
    # TODO: Resource ID에 대한 권한 체크 로직 추가 (RBAC)

    print(f"SUCCESS: User {user_id} accessed resource {resource_id}. Data processing started.")
    return {"status": "success", "message": f"Data for {resource_id} retrieved successfully by {user_id}.", "data": [1, 2, 3]}