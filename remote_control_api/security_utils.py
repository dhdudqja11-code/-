from fastapi import Depends, HTTPException, Security
from typing import Annotated
from passlib.context import CryptContext
from schemas import Role, UserCredentials

# 🚨 중요: 실제 환경에서는 Redis나 DB에서 토큰/권한을 검증해야 합니다. 여기는 더미 구현입니다.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 해시하여 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(credentials: UserCredentials):
    """
    [OAuth 2.0 Dummy] 사용자 인증을 시뮬레이션하고 토큰을 발행하는 로직입니다.
    실제로는 DB에서 유저 정보를 가져와 패스워드 검증 후 JWT를 발급해야 합니다.
    """
    # 더미 검증: username='admin' and password='secure' 일 때만 성공 가정
    if credentials.username != "admin" or credentials.password != "secure":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print("✅ Auth Service: User authenticated successfully.")
    # 실제로는 JWT를 반환해야 하지만, 여기서는 사용자를 직접 반환합니다.
    return {"username": credentials.username, "role": Role.ADMIN}

def get_current_user_with_rbac(
    credentials: Annotated[UserCredentials, Security()], 
    required_role: Role
):
    """
    [RBAC Dummy] 현재 사용자의 역할을 검사하고 필요한 권한이 있는지 확인합니다.
    OAuth 토큰을 통해 유저 정보를 가져오는 과정이 생략되어 있습니다.
    """
    user = get_current_user(credentials) # 먼저 인증 수행
    
    # Role Hierarchy: ADMIN > OPERATOR > VIEWER
    roles_order = {Role.VIEWER: 1, Role.OPERATOR: 2, Role.ADMIN: 3}

    if roles_order[user["role"]] < roles_order[required_role]:
        raise HTTPException(status_code=403, detail=f"Permission Denied. Requires {required_role} role.")
    
    print(f"✅ RBAC Check: User '{user['username']}' passed check for role '{required_role}'.")
    return user

# ⚠️ 주의: 이 함수는 실제 토큰 파싱 및 검증을 수행하는 것이 아니라,
# FastAPI 의존성 주입 테스트를 위해 Dummy로 사용됩니다.
```

### 💻 Step 2: 핵심 API 엔드포인트 구현 (`main.py`)

이제 `FastAPI` 앱을 초기화하고 세 가지 필수 엔드포인트를 연결하겠습니다.

<create_file path="c:\Users\user\AI 기업 두뇌\내 작업들\remote_control_api\main.py">
from fastapi import FastAPI, Depends, HTTPException, status
from schemas import UserCredentials, Token, SessionDetails, CommandInput, CommandResult, Role
from security_utils import get_current_user, get_current_user_with_rbac

app = FastAPI(title="Remote Control API Gateway")

# --- 1. Authentication Endpoint (OAuth 2.0) ---
@app.post("/auth/token", response_model=Token, summary="사용자 자격 증명으로 인증 토큰 발급 (Dummy)")
async def login_for_access_token(credentials: UserCredentials):
    """
    [Auth] 사용자 이름과 비밀번호를 제출하여 API 접근 토큰을 요청합니다. 
    실제로는 JWT를 발행하고, 이 토큰이 모든 요청의 Authorization 헤더에 포함됩니다.
    """
    try:
        # 실제 인증 로직 실행 (get_current_user 내부에서 검증 수행)
        user = get_current_user(credentials) 
        
        # Dummy Token Generation: 만료 시간을 가정하여 토큰 구조 반환
        return Token(access_token="dummy_jwt_" + user['username'], token_type="bearer", expires_to=1678886400)

    except HTTPException as e:
        raise e


# --- 2. Session Start Endpoint (RBAC 적용) ---
@app.post("/session/start", response_model=SessionDetails, summary="새로운 원격 제어 세션 시작")
async def start_remote_session(
    user_info: dict = Depends(get_current_user_with_rbac), # Dummy Token 검증 및 RBAC 적용
):
    """
    [Session] 유효한 토큰을 가진 사용자가 새로운 원격 제어 세션을 시작합니다. 
    세션 ID는 감사 추적(Audit Trail)의 시발점이 됩니다.
    """
    user_role = user_info['role']
    session_id = f"sess_{hash(str(user_info['username']) + str(user_role)) % 1000}"
    
    # [감사 추적 시작] 세션 생성 시점과 주체를 기록합니다.
    print(f"🚀 Session Started: {session_id} by {user_info['username']} (Role: {user_role})")

    return SessionDetails(
        session_id=session_id, 
        user_role=user_role, 
        is_active=True
    )


# --- 3. Command Execution Endpoint (최고 권한 및 Audit/Purge 로직 필수) ---
@app.post("/execute_command", response_model=CommandResult, summary="원격 명령 실행 및 결과 기록")
async def execute_command(
    command_input: CommandInput,
    user_info: dict = Depends(get_current_user_with_rbac), # 최고 권한 검증 필요
):
    """
    [Execution] 원격 제어 명령어의 실행을 시뮬레이션합니다. 
    최소 운영자(OPERATOR) 이상의 권한이 요구됩니다.
    실행 결과는 반드시 감사 추적에 기록되어야 합니다.
    """
    # [RBAC Check]: 명령 수행에는 최소 OPERATOR 레벨 이상이 필요하다고 가정합니다.
    if user_info['role'] != Role.ADMIN and user_info['role'] != Role.OPERATOR:
        raise HTTPException(status_code=403, detail="Permission Denied. Requires OPERATOR role or higher.")

    print(f"⚙️ Executing Command: '{command_input.command}' by {user_info['username']} in session...")
    
    # Dummy Logic Execution Simulation
    if "list users" in command_input.command.lower():
        result = {"success": True, "output_data": "User List: [alice@corp.com, bob@corp.com]"}
    else:
        result = {"success": False, "output_data": None, "error_message": f"Unknown command: {command_input.command}"}

    # 🚨 핵심 로직: 감사 추적(Audit Trail) 기록 및 데이터 파기 프로토콜 반영
    audit_log = {
        "timestamp": "현재 시간", # 실제로는 datetime.now() 사용
        "executor": user_info['username'],
        "session_id": "현재 세션 ID (Placeholder)", 
        "command": command_input.command,
        "outcome": "SUCCESS" if result["success"] else "FAILURE"
    }

    # 반환되는 결과물에는 감사 추적 정보가 포함되지만, 실제 민감 데이터는 별도 로그 시스템에 전송/저장됩니다.
    return CommandResult(
        success=result["success"], 
        output_data=result["output_data"], 
        error_message=result["error_message"], 
        audit_log_entry=audit_log
    )

# --- API Gateway 레벨에서 실행될 테스트/유틸리티 엔드포인트 (Optional) ---
@app.get("/status")
async def get_system_status():
    return {"service": "Remote Control Core", "status": "Operational"}