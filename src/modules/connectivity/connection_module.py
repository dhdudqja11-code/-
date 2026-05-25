# -*- coding: utf-8 -*-
import time
import requests
from typing import Dict, Any, Optional

# --- 🔑 전역 설정 및 예외 정의 (Guardrail & Compliance Focus) ---

class ConnectionError(Exception):
    """연결 과정에서 발생하는 모든 오류를 포괄하는 커스텀 에러."""
    pass

class AuthenticationFailed(ConnectionError):
    """인증 실패 시 발생. 자격 증명 오류."""
    pass

class MfaRequiredError(ConnectionError):
    """다단계 인증(MFA) 검증이 요구되거나 실패했을 때 발생."""
    pass

class QuotaExceededError(ConnectionError):
    """사용량 제한 초과 시 발생. 가장 중요한 Guardrail 중 하나."""
    def __init__(self, remaining: int = 0):
        super().__init__("사용량 한도를 초과했습니다. 다음 주기까지 대기해 주십시오.")
        self.remaining = remaining


# --- 🚀 Core Logic: 접속 및 보안 검증 모듈 (Service Layer) ---

class ConnectionModule:
    """
    원격 제어 API Gateway와 실질적인 HTTP 통신을 수행하며,
    규제 준수(AuthN, PoLP, Quota, MFA) 가드레일을 강제하는 접속 모듈입니다.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')

    def login(self, username: str, password: str) -> str:
        """
        [NFR-1] Gateway 인증 서비스에 로그인하여 JWT Access Token을 발급받습니다.
        """
        login_url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}
        
        try:
            print(f"-> [Auth]: Attempting login to {login_url}...")
            response = requests.post(login_url, json=payload, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationFailed("사용자 ID 또는 비밀번호가 유효하지 않습니다. (401 Unauthorized)")
            
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            
            if not token:
                raise AuthenticationFailed("인증 토큰 발급에 실패하였습니다. 응답 값이 비어있습니다.")
                
            print("✅ [Auth]: JWT Access Token received successfully.")
            return token
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"인증 게이트웨이 서버 연결 실패: {e}")

    def fetch_protected_data(self, token: str, resource_id: str) -> Dict[str, Any]:
        """
        [NFR-2 / NFR-3] 발급받은 JWT 토큰을 이용하여 보호된 자원에 접근합니다.
        이 단계에서 권한 위반(PoLP), 쿼터 초과(Quota), MFA 요구 사항이 걸러집니다.
        """
        data_url = f"{self.base_url}/api/v1/data/{resource_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"-> [API Request]: Accessing protected resource {resource_id}...")
            response = requests.get(data_url, headers=headers, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationFailed("세션 토큰이 만료되었거나 올바르지 않습니다.")
            elif response.status_code == 403:
                raise MfaRequiredError("MFA(다단계 인증)가 설정되지 않았거나 검증에 실패했습니다. (403 Forbidden)")
            elif response.status_code == 429:
                raise QuotaExceededError(remaining=0)
                
            response.raise_for_status()
            print(f"🎉 [API Request]: Successfully accessed resource {resource_id}.")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"보호 리소스 서버 통신 실패: {e}")


def establish_secure_connection(
    username: str, 
    password: str, 
    resource_id: str, 
    base_url: str = "http://127.0.0.1:8000"
) -> Dict[str, Any]:
    """
    인프라 계층(FastAPI Gateway)과 연동하여 인증부터 리소스 조회까지의 
    전체 보안 파이프라인을 실질적으로 수행하는 단일 진입점 헬퍼 함수입니다.
    """
    module = ConnectionModule(base_url)
    
    # 1. 로그인 수행 및 JWT 토큰 획득
    token = module.login(username, password)
    
    # 2. 보호된 자원 획득 시도 (MFA, Quota, PoLP 가드레일 자동 필터링)
    result = module.fetch_protected_data(token, resource_id)
    return result


# --- 🧪 로컬 단독 테스트 시뮬레이션용 코드 ---
if __name__ == "__main__":
    print("--- [Connection Module Standalone Simulation] ---")
    # 예시 구동 (실무 연결 시에는 백엔드가 구동 중이어야 작동함)
    try:
        data = establish_secure_connection("admin", "PASSWORD_HERE", "system_status")
        print(f"✅ Success Data: {data}")
    except ConnectionError as e:
        print(f"❌ Failed Securely: {type(e).__name__} - {e}")
