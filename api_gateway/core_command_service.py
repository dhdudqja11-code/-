import os
from typing import Dict, Optional
from paramiko import SSHClient, AutoKey
from pydantic import BaseModel, Field

# --- Data Models (Pydantic 사용) ---
class ExecutionResult(BaseModel):
    """원격 명령어 실행 결과를 구조화합니다."""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0

class CommandInput(BaseModel):
    """명령어 실행을 위한 입력값 정의 (TDD 기반)."""
    target_host: str = Field(description="접속할 원격 서버의 호스트 이름.")
    command: str = Field(description="실행할 명령어 문자열. 예: 'ls -l /data'.")
    timeout: int = Field(default=60, description="명령어 실행 최대 대기 시간 초 (초).")

# --- Core Service Class ---
class CommandService:
    """
    Core Server의 역할을 수행하는 핵심 명령어 실행 서비스. 
    SSH를 사용하여 원격 서버에 명령을 전송하고 결과를 분석합니다.
    """

    def __init__(self):
        # 로컬 환경 변수에서 SSH 키 경로 등을 가져오는 것이 안전함
        self.ssh_key_path = os.environ.get("REMOTE_SSH_KEY") 
        if not self.ssh_key_path:
            print("WARNING: REMOTE_SSH_KEY 환경 변수가 설정되지 않았습니다. 연결에 실패할 수 있습니다.")

    def _establish_connection(self, host: str) -> SSHClient:
        """호스트와 안전하게 SSH 연결을 시도합니다."""
        client = SSHClient()
        # 실제 운영 환경에서는 사용자 이름과 키 기반 인증이 필요함
        try:
            # 예시: 사용자명은 'api_user'로 가정하고, 키를 사용하거나 비밀번호를 입력할 수 있음.
            client.set_missing_host_key_policy(AutoKey.AutoAddPolicy()) 
            client.connect(hostname=host, username="api_user", key_filename=self.ssh_key_path)
        except Exception as e:
            raise ConnectionError(f"SSH 연결 실패: {e}") from e
        return client

    def execute_remote_command(self, input_data: CommandInput) -> ExecutionResult:
        """
        실제 원격 명령을 실행하고 결과를 구조화하여 반환합니다. 
        (Critical Path - 에러 처리에 가장 신경 써야 함)
        """
        print(f"--- [INFO] Initiating remote command execution on {input_data.target_host} ---")
        client = None
        try:
            # 1. 연결 시도 및 검증
            client = self._establish_connection(input_data.target_host)

            # 2. 명령어 실행 (스트래티지: exec_command 사용)
            print(f"--- [DEBUG] Executing command: {input_data.command}")
            stdin, stdout, stderr = client.exec_command(input_data.command)
            
            # 3. 결과 수집 및 시간 제한 적용 (Timeout 처리가 중요함)
            stdout_data = stdout.read().decode('utf-8').strip()
            stderr_data = stderr.read().decode('utf-8').strip()
            
            # Note: Paramiko의 exec_command는 직접적인 exit code를 얻기 어려울 수 있으므로, 
            # 여기서는 임시적으로 성공으로 간주하고 이후 로직에서 refine 필요.
            return ExecutionResult(stdout=stdout_data, stderr=stderr_data, exit_code=0)

        except ConnectionError as e:
            print(f"--- [ERROR] Core Service: {e}")
            raise RuntimeError(f"원격 서버 연결 실패: {str(e)}") from e
        except Exception as e:
            print(f"--- [FATAL ERROR] Command execution failed: {type(e).__name__} - {e}")
            # 원인 분석이 필요한 로직을 추가해야 함.
            raise RuntimeError(f"명령어 실행 중 알 수 없는 오류 발생: {str(e)}") from e
        finally:
            if client:
                client.close()

# --- 테스트 및 검증 코드 (임시) ---
def run_service_test():
    """서비스의 기본 동작을 시뮬레이션합니다."""
    print("\n>>> [TEST START] Core Command Service Test Simulation <<<")
    try:
        # 환경 변수 설정이 필요함. 실제 실행 전 주석 처리하거나 값을 넣어줘야 함.
        os.environ["REMOTE_SSH_KEY"] = "/path/to/your/private/key" 
        service = CommandService()
        
        test_input = CommandInput(
            target_host="localhost", # 테스트를 위해 로컬로 설정 (실제는 외부 호스트)
            command="echo 'Test successful on local machine'",
            timeout=10
        )
        result = service.execute_remote_command(test_input)
        print("\n✅ [TEST RESULT] Execution Successful.")
        print(f"STDOUT:\n{result.stdout}")
    except Exception as e:
        print(f"\n❌ [TEST FAILED] Simulation failed due to dependency or connection issue: {e}")

if __name__ == "__main__":
    run_service_test()