from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
from typing import Dict, Any
# 임포트 가정: 실제로는 JWT 검증 및 리스크 계산 모듈이 필요함

# ------------------- [1. 데이터 모델 정의] ------------------- #
class MiniROIRequest(BaseModel):
    """Mini ROI 시뮬레이션 요청 바디."""
    user_id: str
    data_source: Dict[str, Any]

class AuditBlock(BaseModel):
    """모든 API 응답에 강제되는 불변 감사 기록 구조체."""
    status: str # SUCCESS or FAILURE
    timestamp_utc: str
    transaction_id: str = None
    audit_details: Dict[str, Any]
    message: str

# ------------------- [2. 가짜 의존성 및 유틸리티 함수 정의] ------------------- #

def get_current_time() -> str:
    """UTC 시간 포맷팅 (실제로는 datetime 사용)."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def authenticate_user(token: str = Depends(...)) -> Dict[str, str]:
    """
    JWT 인증 및 인가 로직을 시뮬레이션합니다. (실제 구현 필요)
    실패 시 401/403 발생.
    """
    if not token or "Bearer" not in token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or Invalid Token.")
    # 실제 로직: JWT 검증 (exp, signature, iss) 및 Role 추출
    print("✅ [AuthN] Token validated successfully.") 
    return {"user_id": "test-user", "roles": ["ROLE_USER"]}

def generate_audit_block(status: str, details: Dict[str, Any], result_payload: Any = None) -> AuditBlock:
    """모든 트랜잭션 결과를 표준화된 AuditBlock으로 포장합니다."""
    return AuditBlock(
        status=status,
        timestamp_utc=get_current_time(),
        transaction_id=str(uuid.uuid4()),
        audit_details={
            "source_api": "Unknown", # 실제 호출된 API 경로로 변경되어야 함
            "initiator_user_id": details.get("user_id"),
            "requested_action": "Mini ROI Simulation",
            "result_summary": f"{status} processed.",
        },
        message=f"Audit Block generated for {status} transaction."
    )

# ------------------- [3. FastAPI 애플리케이션 및 엔드포인트] ------------------- #
app = FastAPI(title="Immutable Audit Gateway")

@app.post("/api/v1/simulate_risk", response_model=AuditBlock)
async def simulate_risk_endpoint(
    request: MiniROIRequest, 
    auth_user: Dict[str, str] = Depends(authenticate_user) # JWT 검증 의존성 주입
):
    """
    Mini ROI 시뮬레이션을 실행하고 반드시 AuditBlock을 반환하는 핵심 트랜잭션 엔드포인트.
    """
    print(f"⚙️ [API Call] Received request from {auth_user['user_id']} for simulation.")

    # 1. 리스크 계산 로직 (가정)
    try:
        # --- 실제 비즈니스 로직이 들어가는 곳 ---
        mini_roi_score = len(request.data_source) * 0.9
        detected_risks = ["Data Integrity", "Compliance Gap"] if mini_roi_score > 1.5 else []
        # --------------------------------------

        if not detected_risks:
             raise Exception("Simulation failed due to internal calculation error.")

        result_payload = {
            "mini_roi_score": round(mini_roi_score, 3),
            "detected_risks": detected_risks
        }
        
        # 2. 성공적인 경우 AuditBlock 생성 및 반환
        audit_details = {"user_id": request.user_id, "source_api": "/api/v1/simulate_risk"}
        return generate_audit_block(status="SUCCESS", details=audit_details, result_payload=result_payload)

    except Exception as e:
        # 3. 실패하는 경우에도 AuditBlock을 생성하여 '오류 자체'를 기록
        print(f"🐛 [Error] Simulation failed: {e}")
        error_message = str(e)
        audit_details = {"user_id": request.user_id, "source_api": "/api/v1/simulate_risk"}
        return generate_audit_block(status="FAILURE", details=audit_details, message=f"Failure: {error_message}")

# ------------------- [4. 테스트 명령어] ------------------- #
# 참고: 이 파일은 실제 서버 실행을 위해 사용됩니다.
# 터미널에서 uvicorn core_gateway.main_api:app --reload 명령으로 실행 가능합니다.