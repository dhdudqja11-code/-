import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header

# -------------------------------------------------
# [Config] - 보안 및 제한 설정 (HARDCODED 임시)
RATE_LIMIT_WINDOW = 60  # 초 단위
MAX_REQUESTS_PER_USER = 10 # 분당 최대 요청 수

# 가상의 권한 정의: User Role -> Allowed Endpoint/Action
# PoLP의 핵심입니다. 사용자 역할에 따라 접근 가능한 기능만 명시합니다.
PRIVILEGE_MATRIX = {
    "admin": {"read_data", "write_data", "manage_user"},
    "premium": {"read_data", "write_data"},
    "basic": {"read_data"}
}

# 인메모리 저장소 (실제 환경은 Redis 사용 권장)
REQUEST_COUNT: Dict[str, list] = {} 
LAST_ACCESS: Dict[str, float] = {}


app = FastAPI(title="Core API Gateway", description="OAuth 2.0 기반 게이트웨이 및 보안 로직 테스트베드")

# -------------------------------------------------
# [Middleware] - Rate Limiting & PoLP Enforcement
def rate_limit_checker(user_id: str = Header(...)):
    """
    사용자 ID를 받아 요청 제한을 확인하는 미들웨어.
    Rate Limit 초과 시 HTTP 429 Too Many Requests 발생.
    """
    current_time = time.time()
    
    if user_id not in REQUEST_COUNT:
        REQUEST_COUNT[user_id] = []
        LAST_ACCESS[user_id] = current_time

    # 윈도우 기반 요청 카운트 유지 (Rate Limiting Window)
    # 오래된 타임스탬프 제거 (슬라이딩 윈도우)
    REQUEST_COUNT[user_id] = [t for t in REQUEST_COUNT[user_id] if t > current_time - RATE_LIMIT_WINDOW]

    if len(REQUEST_COUNT[user_id]) >= MAX_REQUESTS_PER_USER:
        # 🚨 Rate Limit 초과! 🐛
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait.")

    # 요청 카운트 업데이트
    REQUEST_COUNT[user_id].append(current_time)
    return user_id


def authenticate_and_authorize(token: str = Header(...)):
    """
    OAuth 2.0 토큰을 검증하고, 사용자 ID와 권한 레벨을 추출하는 함수 (AuthN + PoLP).
    실제로는 JWT 디코딩 및 DB 조회가 필요합니다.
    """
    # 실제 환경에서는 여기서 JWT 유효성 검사(서명, 만료)를 수행해야 합니다.
    if not token or "valid_jwt_" not in token:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token.")

    try:
        # 가상의 토큰 파싱 로직 (예시: valid_jwt_{user_id}:{role})
        parts = token.split("_")[-2:] # 예: jwt_valid_admin
        user_id = parts[0].replace("jwt", "") 
        role = parts[1]

        if role not in PRIVILEGE_MATRIX:
            raise HTTPException(status_code=403, detail="Unknown user role.")
            
        # PoLP 검증을 위해 (user_id, role)를 반환합니다.
        return {"user_id": f"User_{user_id}", "role": role}

    except Exception as e:
        print(f"Authentication failure: {e}")
        raise HTTPException(status_code=401, detail="Token processing failed.")


# -------------------------------------------------
# [API Endpoints] - 게이트웨이 백엔드 로직
@app.get("/api/v1/data/read", dependencies=[Depends(rate_limit_checker), Depends(authenticate_and_authorize)])
def read_data(auth_info: dict):
    """
    데이터 읽기 API. 최소한의 권한으로 접근 가능해야 합니다. (Read-Only)
    Rate Limit 및 Auth/PoLP 검증이 모두 작동합니다.
    """
    role = auth_info['role']
    if "read_data" not in PRIVILEGE_MATRIX[role]:
        # 이 코드는 사실 위에서 걸러져야 하지만, 방어적으로 남깁니다.
        raise HTTPException(status_code=403, detail="Forbidden: Role does not allow reading data.")
    return {"message": f"Data read success for {auth_info['user_id']} (Role: {role})."}

@app.post("/api/v1/data/write", dependencies=[Depends(rate_limit_checker), Depends(authenticate_and_authorize)])
def write_data(auth_info: dict, payload: Dict[str, Any]):
    """
    데이터 쓰기 API. 높은 권한이 필요합니다. (Write Operation)
    Rate Limit 및 Auth/PoLP 검증이 모두 작동합니다.
    """
    role = auth_info['role']
    if "write_data" not in PRIVILEGE_MATRIX[role]:
        # 🚨 PoLP 실패: 권한 미달! (가장 중요한 테스트 포인트)
        raise HTTPException(status_code=403, detail="Forbidden: Role does not allow writing data.")
    
    return {"message": f"Data written successfully by {auth_info['user_id']} (Role: {role})."}

@app.delete("/api/v1/admin/manage")
def manage_endpoint(auth_info: dict):
    """
    관리자 전용 엔드포인트. 가장 높은 권한만 접근 가능해야 합니다.
    Rate Limit은 관리자도 적용되지만, PoLP는 이 API 자체가 방어합니다.
    """
    role = auth_info['role']
    if role != "admin":
        # 🚨 PoLP 실패: Admin 역할이 아니면 절대 도달하면 안 됩니다.
        raise HTTPException(status_code=403, detail="Forbidden: Only 'admin' can access this endpoint.")
        
    return {"message": f"Admin action executed by {auth_info['user_id']}."}