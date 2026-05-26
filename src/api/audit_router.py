from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import datetime
import jwt # Assuming PyJWT is installed

# --- Mock Dependencies & Services (실제 환경에 맞게 구현 필요) ---
# ⚠️ 코다리: 이 부분은 실제 JWT 검증/DB 접근 로직으로 대체되어야 합니다.
def get_current_user(token: str = Depends(lambda: None)):
    """JWT Token을 받아 사용자 정보를 반환하는 의존성 함수 (Mocked)."""
    try:
        # 실제로는 헤더에서 Bearer 토큰을 추출하여 검증해야 함.
        if not token or "secure" not in token:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials.")
        return {"user_id": 123, "role": "admin", "is_active": True}
    except Exception as e:
        # 실제로는 JWT 디코딩 실패나 만료가 여기서 처리됨.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed or token expired.")


class TransactionData(BaseModel):
    """API로 수신될 트랜잭션 데이터 구조."""
    source: str = Field(description="트랜잭션의 출처 (e.g., Webhook/Manual)")
    data_payload: dict = Field(description="실제 처리할 비즈니스 페이로드.")
    user_action: str = Field(description="사용자의 행동 유형 (예: 구매, 조회, 설정변경).")


class AuditBlock(BaseModel):
    """법적 증명력을 담보하는 감사 블록 응답 구조."""
    success: bool
    transaction_id: str
    timestamp: datetime.datetime
    status_code: int # 200 for success, 4xx/5xx for failure
    message: str
    audit_data: dict = Field(description="감사 기록에 포함된 상세 데이터.")


def immutable_audit_gateway(transaction_data: TransactionData, user_info: dict) -> AuditBlock:
    """
    [핵심 로직] Immutable Audit Gateway (IAG)를 시뮬레이션합니다.
    이 함수는 실제 체이닝 해싱 및 법적 무결성 검증을 수행하는 역할을 합니다.
    (실제 구현은 이전에 작성된 IAG 서비스를 사용해야 함.)
    """
    print(f"--- [IAG] Processing transaction for user {user_info['user_id']} ---")

    # 1. 필수 유효성 검사 (Guard Clause)
    if not transaction_data.source or "payload" not in transaction_data.data_payload:
        return AuditBlock(
            success=False,
            transaction_id="N/A",
            timestamp=datetime.datetime.utcnow(),
            status_code=400,
            message="[ERROR] Required source or payload missing.",
            audit_data={"validation_failed": True}
        )

    # 2. 가상 리스크 검증 (예외 시뮬레이션)
    if "illegal_action" in transaction_data.user_action:
         return AuditBlock(
            success=False,
            transaction_id="N/A",
            timestamp=datetime.datetime.utcnow(),
            status_code=403,
            message="[SECURITY ALERT] Illegal action detected. Transaction blocked due to potential regulatory violation.",
            audit_data={"alert_type": "Regulatory Violation", "reason": "Illegal Action"}
        )

    # 3. 성공 로직 시뮬레이션
    transaction_id = f"TX-{hash(str(transaction_data)) % 10000}"
    return AuditBlock(
        success=True,
        transaction_id=transaction_id,
        timestamp=datetime.datetime.utcnow(),
        status_code=200,
        message="[SUCCESS] Transaction processed and immutable audit record created.",
        audit_data={"hash": "ABCDE12345", "source": transaction_data.source}
    )


# --- FastAPI Router Definition ---

router = APIRouter(prefix="/v1/audit", tags=["Audit Gateway"])

@router.post("/process", response_model=AuditBlock, status_code=status.HTTP_200_OK)
async def process_transaction(
    data: TransactionData, 
    current_user: dict = Depends(get_current_user) # 인증 의존성 주입
):
    """
    POST /v1/audit/process 엔드포인트. 트랜잭션 데이터를 수신하여 IAG를 거쳐 감사 기록을 생성합니다.
    """
    try:
        # 1. 권한 검증 (Authorization)
        if current_user['role'] != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permission to process audit.")

        # 2. 핵심 로직 호출
        audit_result = immutable_audit_gateway(data, current_user)
        
        return audit_result # 성공 시 AuditBlock 반환

    except HTTPException as e:
        # 인증/권한 실패는 FastAPI의 HTTP Exception으로 처리되도록 재발사.
        raise e 
    except Exception as e:
        # 예상치 못한 서버 오류 발생 시, 안전하게 AuditBlock 구조를 갖춘 에러 응답을 반환합니다.
        print(f"CRITICAL ERROR during audit processing: {e}")
        return AuditBlock(
            success=False,
            transaction_id="SERVER-FAIL",
            timestamp=datetime.datetime.utcnow(),
            status_code=500,
            message=f"[FATAL] Internal Server Error. Please contact support with details.",
            audit_data={"error_type": type(e).__name__, "details": str(e)[:100]}
        )

# ---------------------------------------------
# API 테스트를 위한 FastAPI 앱 인스턴스 (실제 서버 실행 시 필요)
from fastapi import FastAPI
app = FastAPI(title="Audit Gateway Service")
app.include_router(router)
# ---------------------------------------------