from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import time
from typing import Literal
# 로컬 파일 경로 사용 (최근 생성된 파일을 참조)
from src.services.authority_manager.authority_state_manager import AuthorityStateManager

app = FastAPI(title="Authority Gateway", version="v1")

# -------------------------
# Pydantic Schemas for Data Contract Enforcement
# 모든 요청과 응답은 스펙에 따라 구조화되어야 합니다. [근거: 💻 코다리 개인 메모리]
# -------------------------

class AuthorityCheckRequest(BaseModel):
    """외부에서 들어오는 트랜잭션 데이터 및 리스크 지표."""
    transaction_id: str  # 고유 트랜잭션 ID
    risk_score: float    # 현재 위험 점수 (0.0 ~ 1.0)
    data_source: str     # 데이터 출처 (예: Webhook, Manual Input)
    is_critical_system: bool = False # 핵심 시스템 관련 여부

class AuthorityCheckResponse(BaseModel):
    """시스템 응답 스키마. 모든 상태에 공통적으로 사용되는 구조."""
    status: Literal["IDLE", "WARNING", "AUTHORITY"]  # 현재 권위 상태
    authority_score: float
    timestamp: float = time.time() # 검증 시점 (추적 가능성 확보)
    message: str

    # WARNING 상태에서만 필수적으로 포함되어야 하는 구조체 [근거: 🏢 회사 정체성]
    warning_details: dict | None = None 


@app.post("/api/v1/authority/check_score", response_model=AuthorityCheckResponse)
async def check_authority_score(request: AuthorityCheckRequest):
    """
    트랜잭션 데이터 기반으로 권위 점수를 체크하고 시스템 상태를 결정하는 핵심 엔드포인트.
    FAILURE PATH에서도 통제권을 잃지 않도록 설계되어야 합니다. [근거: 🏢 회사 정체성]
    """
    try:
        # 1. 상태 관리자 초기화 및 로직 실행
        state_manager = AuthorityStateManager()
        current_state, score, warning_info = state_manager.evaluate(request)

        response = AuthorityCheckResponse(
            status=current_state,
            authority_score=score,
            message=f"Authority Check Successful. Status: {current_state}"
        )

        # 2. WARNING 상태에 대한 기술적 강제 구현 (불안감 고조)
        if current_state == "WARNING":
            # Warning Details를 필수적으로 채워서 클라이언트가 이를 무시할 수 없게 함.
            response.warning_details = {
                "severity": "CRITICAL", # 심각도 명시
                "required_action": warning_info["action"], # 필요한 행동 강제 제시
                "explanation": warning_info["reason"] # 구조적 원인 분석 제공
            }
            # WARNING 상태에서는 1초의 인위적인 지연을 두어, 시스템이 '생각하는' 시간을 부여함. [근거: 💻 코다리 개인 메모리]
            await asyncio.sleep(1.0) 
            response.message = "🚨 AUTHORITY WARNING! 임계치 근접 감지. 즉시 조치가 필요합니다."

        elif current_state == "AUTHORITY":
             # 성공적으로 Authority 상태에 진입하면, 강한 확신을 주는 메시지를 사용함.
            pass # 기본 응답 객체 유지

        return response

    except Exception as e:
        # 3. 시스템 장애 발생 시 (최후의 방어선)
        print(f"🚨 SYSTEM FAILURE DETECTED: {e}")
        raise HTTPException(status_code=503, detail={
            "error": "SYSTEM_UNAVAILABLE",
            "message": "시스템이 현재 권위 점수 계산에 실패했습니다. 관리자에게 문의하십시오.",
            "suggested_action": "잠시 후 재시도하거나 다른 데이터 소스를 이용해 주십시오." # 해결책 강제 제시
        })

# 테스트를 위해 asyncio import 추가 (FastAPI 환경 고려)
import asyncio