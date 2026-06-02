import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Logging 설정 (진단 용이성을 위해 상세 로그 레벨 유지)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RemoteAccessService")

class AccessToken(BaseModel):
    """사용자의 인증 및 권한 정보를 담는 가상 토큰."""
    user_id: str = Field(description="User's unique identifier.")
    role: str = Field(description="접근 역할 (admin, standard, guest).")
    is_authenticated: bool = True

class RemoteConnectionDetails(BaseModel):
    """원격 접속 세션 정보를 담는 모델."""
    ip_address: str
    port: int

class IntegrationError(Exception):
    """통합 기능 프로토타입에서 발생하는 모든 오류를 처리하는 커스텀 예외 클래스."""
    def __init__(self, message: str, error_type: str = "GENERAL_ERROR"):
        super().__init__(message)
        self.error_type = error_type

# --- 1. connect-remote 엔드포인트 로직 (접속 및 권한 검증) ---
def connect_remote(token: AccessToken, connection_info: RemoteConnectionDetails) -> Dict[str, Any]:
    """
    원격 연결을 시도하고 기본적인 권한과 네트워크 상태를 확인합니다.
    실패 시 IntegrationError 발생 (RBAC 실패 또는 네트워크 오류).
    """
    logger.info(f"Attempting connection for user {token.user_id} with role {token.role}")

    # [🔑 RBAC 검증] 관리자 권한이 없으면 특정 기능 접속 자체가 제한될 수 있음 (가정)
    if token.role == "guest":
        raise IntegrationError("Guest user는 원격 연결 시도가 불가능합니다.", "AUTH_ERROR")
    
    # [🌐 네트워크 가상 검증] IP 포맷 유효성 및 접근 가능 여부 체크
    try:
        ip = connection_info.ip_address
        port = connection_info.port
        if not ("192." <= ip[:4]) or not (1024 <= port <= 65535):
            raise IntegrationError("유효하지 않거나 제한된 IP/Port 조합입니다.", "NETWORK_ERROR")

    except Exception as e:
        logger.error(f"Connection validation failed: {e}")
        raise IntegrationError(f"연결 정보 유효성 검증 실패: {str(e)}", "VALIDATION_ERROR")

    # 성공 시 가상 세션 ID 반환
    session_id = f"SESSION-{token.user_id}-{hash(ip + str(port)) % 1000}"
    logger.info(f"Successfully established connection. Session ID: {session_id}")
    return {"status": "connected", "session_id": session_id, "details": f"Connected to {connection_info.ip_address}:{connection_info.port}."}

# --- 2. execute-command 엔드포인트 로직 (명령 실행 및 권한 검증) ---
def execute_command(token: AccessToken, session_id: str, command: str) -> Dict[str, Any]:
    """
    활성 세션 ID를 기반으로 원격 명령을 실행합니다.
    실패 시 IntegrationError 발생 (권한 부족 또는 명령어 구문 오류).
    """
    logger.info(f"Executing command '{command[:20]}...' for session {session_id} by role {token.role}")

    # [🔑 RBAC 검증] 'root' 명령이나 시스템 설정을 건드리는 명령은 관리자만 허용 (가정)
    if "systemctl restart" in command and token.role != "admin":
        raise IntegrationError("관리자 권한이 필요합니다. 이 명령어는 접근 제한되었습니다.", "PERMISSION_DENIED")

    # [⚙️ 실행 로직 시뮬레이션] 특정 키워드에 따른 성공/실패 분기
    if "FAIL_CMD" in command:
        logger.warning(f"Simulated Command Execution Failure for {session_id}.")
        raise IntegrationError("원격 시스템에서 명령을 실행하는 중 오류가 발생했습니다. 구문을 확인해주세요.", "EXECUTION_ERROR")

    # 성공적인 명령어 실행 결과 반환
    result = f"SUCCESS: Command '{command}' executed successfully on remote system. Output code 0."
    return {"status": "success", "executed_command": command, "output": result}

# --- 3. stream-data 엔드포인트 로직 (데이터 스트리밍 및 종료) ---
def stream_data(token: AccessToken, session_id: str) -> Dict[str, Any]:
    """
    원격 세션에서 로그나 실시간 데이터를 스트림으로 받아와 종료합니다.
    세션 유효성 검증이 핵심입니다.
    """
    logger.info(f"Attempting to stream data for session {session_id} by user {token.user_id}")

    # [🔗 세션 유효성 검사] 가상의 세션 ID 패턴을 이용해 무효화 체크 (가정)
    if not str(session_id).startswith("SESSION-"):
        raise IntegrationError("유효하지 않거나 만료된 세션 ID입니다.", "TIMEOUT_ERROR")

    # 데이터 스트리밍 성공 시뮬레이션
    data_stream = [
        "--- Start Data Stream ---\n",
        f"[{token.role}]: System metrics received. CPU Load: 35%, Memory: 60%.\n",
        "------------------------\n",
        "Data streaming completed successfully."
    ]
    return {"status": "stream_complete", "data": "\n".join(data_stream)}

# --- 통합 검증을 위한 API Gateway Mock 함수 (사용자가 실제로 호출할 로직) ---
def run_remote_access_flow(token: AccessToken, connection_info: RemoteConnectionDetails, command: str):
    """전체 원격 접근 플로우를 시뮬레이션합니다."""
    try:
        # 1. 연결 (connect-remote)
        conn_result = connect_remote(token, connection_info)
        session_id = conn_result['session_id']

        # 2. 명령 실행 (execute-command)
        cmd_result = execute_command(token, session_id, command)
        
        # 3. 데이터 스트리밍 및 종료 (stream-data)
        stream_result = stream_data(token, session_id)

        return {
            "success": True,
            "report": "✅ 원격 접근 플로우가 성공적으로 완료되었습니다.",
            "details": {
                "connection": conn_result,
                "command_output": cmd_result,
                "data_stream": stream_result
            }
        }

    except IntegrationError as e:
        # 통합 오류 발생 시 모든 단계가 실패했음을 명확히 보고함.
        return {
            "success": False,
            "error_report": f"❌ 원격 접근 플로우 중 치명적인 오류 발생 ({e.error_type}).",
            "details": str(e)
        }
    except Exception as e:
        # 예측하지 못한 시스템 레벨의 예외 처리 (Fail-safe)
        return {
            "success": False,
            "error_report": f"🚨 예상치 못한 시스템 에러 발생. 디버깅 필요 ({type(e).__name__}).",
            "details": str(e)
        }

# --- 테스트 코드를 위한 예시 (실제 프로젝트에서는 test 파일에 분리됨) ---
def run_validation_test():
    """모든 엔드포인트의 핵심 로직을 검증하는 테스트 함수."""
    print("\n--- [✅ 통합 기능 프로토타입 검증 시작] ---")
    
    # 1. 성공 케이스 테스트 (Admin)
    admin_token = AccessToken(user_id="ceo", role="admin")
    conn_info_ok = RemoteConnectionDetails(ip_address="192.168.1.50", port=22)
    print("\n[테스트 1: 성공 케이스 (Admin)]...")
    result_success = run_remote_access_flow(admin_token, conn_info_ok, "ls -l /var/log")
    print(f"   -> 결과: {result_success['report']}")

    # 2. 권한 부족 케이스 테스트 (Standard User -> Root 명령 시도)
    standard_token = AccessToken(user_id="userB", role="standard")
    print("\n[테스트 2: RBAC 실패 (Standard -> Admin Command)]...")
    result_rbac = run_remote_access_flow(standard_token, conn_info_ok, "systemctl restart sshd")
    print(f"   -> 결과: {result_rbac['error_report']}")

    # 3. 인증 오류 케이스 테스트 (Guest User)
    guest_token = AccessToken(user_id="temp", role="guest")
    print("\n[테스트 3: AUTH 실패 (Guest)]...")
    result_auth = run_remote_access_flow(guest_token, conn_info_ok, "echo hello")
    print(f"   -> 결과: {result_auth['error_report']}")

    # 4. 네트워크/명령어 오류 케이스 테스트 (Fail Command)
    user_token = AccessToken(user_id="test", role="admin") # Admin이라도 명령 실패는 별개임
    print("\n[테스트 4: EXECUTION 에러 발생 시뮬레이션]...")
    result_exec = run_remote_access_flow(user_token, conn_info_ok, "FAIL_CMD");
    print(f"   -> 결과: {result_exec['error_report']}")

# 테스트 실행 예시 (실제 사용자는 이 함수를 호출하여 검증)
if __name__ == "__main__":
    run_validation_test()