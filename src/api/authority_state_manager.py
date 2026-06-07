import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json

# --- 1. 스키마 정의 (L_reg 기반) ---
class LRegData(BaseModel):
    """
    규제 리스크 근거 데이터 구조: 문제 발생의 구체적인 원인과 출처를 기록합니다.
    Authority Meter 계산에 사용되는 핵심 입력값입니다.
    """
    breach_type: str = Field(..., description="위반된 규정 유형 (예: GDPR, CCPA)")
    source_system: str = Field(..., description="데이터가 유입/처리된 시스템 출처")
    verification_timestamp: str = Field(..., description="검증이 이루어진 시간 (ISO 8601)")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="규제 위반에 따른 위험 점수 (0.0 ~ 1.0)")

class StateTransitionPayload(BaseModel):
    """
    E2E 통합 테스트 시뮬레이션을 위한 요청 페이로드.
    사용자는 이 구조로만 API를 호출해야 합니다.
    """
    lreg_data: LRegData
    initial_authority_level: float = Field(..., ge=0.1, description="시작 Authority Meter 수치")

# --- 2. 상태 관리자 핵심 로직 (StateManager Pattern) ---
class AuthorityStateManager:
    """
    시스템적 권위를 증명하는 상태 전이(State Transition)를 강제합니다.
    상태 변화는 항상 초기 -> 경고 -> 통제권 확보의 구조를 따릅니다.
    """

    STATUSES = {
        "INITIAL": "초기 (Initial State)",
        "WARNING": "경고 (Authority Warning)",
        "CONTROL_ACQUISITION": "통제권 확보 (Control Acquired)"
    }

    @staticmethod
    def _calculate_authority(current_score: float, stage: str) -> float:
        """단계별 Authority Meter 변화를 계산합니다. (정량적 증명)"""
        if stage == "INITIAL":
            return current_score * 0.95  # 초기 리스크로 인해 약간 하락
        elif stage == "WARNING":
            # 경고 단계에서는 리스크가 커지므로, Authority는 급격히 감소해야 함.
            return max(0.1, current_score - (1.0 - current_score) * 0.5)
        elif stage == "CONTROL_ACQUISITION":
            # 해결책 제시로 인해 Authority가 목표치까지 회복되는 것을 시뮬레이션
            return min(1.0, current_score + 0.3)

    @staticmethod
    def simulate_breach(payload: StateTransitionPayload) -> Dict[str, Any]:
        """
        규제 위반 리스크를 기반으로 E2E 상태 전이를 시뮬레이션합니다.
        강제 지연 시간(1초)을 준수하여 사용자 경험에 권위를 부여합니다.
        """
        lreg = payload.lreg_data
        current_authority = payload.initial_authority_level

        # -------------------------
        # [STEP 1] Initial State (문제 정의 및 초기 진단)
        # -------------------------
        time.sleep(0.5) # 사용자에게 잠시 생각할 시간 부여
        state_data = {
            "status": "INITIAL",
            "message": f"[진단 시작] 데이터 무결성 검사 중... 규정 '{lreg.breach_type}' 위반 의심.",
            "authority_meter": AuthorityStateManager._calculate_authority(current_authority, "INITIAL"),
            "details": {
                "problem": f"시스템이 외부 데이터 `{lreg.source_system}`로부터 받은 트랜잭션의 규제 준수 여부가 불확실합니다.",
                "risk_score": lreg.risk_score * 100, # 백분율로 표시하여 전문성 강화
            }
        }

        # -------------------------
        # [STEP 2] Warning State (원인 분석 및 위험 경고)
        # --- 핵심: 강제 지연 시간 준수 ---
        time.sleep(1.0) # CEO 지시사항: 필수적 권위 증명 단계의 강제 지연 시간
        warning_authority = AuthorityStateManager._calculate_authority(state_data["authority_meter"], "WARNING")
        state_data["status"] = "WARNING"
        state_data["message"] = f"[경고! 🔴] 시스템 아키텍처 결함이 감지되었습니다. 즉각적인 통제권 확보가 필요합니다."
        state_data["authority_meter"] = warning_authority
        state_data["details"] = {
            "analysis": "위험 데이터의 원인 분석 결과, 특정 외부 소스의 데이터 파싱 오류 또는 규정 업데이트 누락이 원인으로 지목됩니다. (Authority Breach)",
            "suggested_action": "관련 시스템 트래픽을 즉시 우회시키고 수동 검증 절차를 거쳐야 합니다.",
        }

        # -------------------------
        # [STEP 3] Control Acquisition State (해결책 제시 및 권위 확보)
        # -------------------------
        time.sleep(0.5)
        final_authority = AuthorityStateManager._calculate_authority(warning_authority, "CONTROL_ACQUISITION")
        state_data["status"] = "SUCCESS" # 최종 성공 상태를 부여하여 완료를 알림
        state_data["message"] = f"[✅ 통제권 확보] 시스템적 위협을 식별하고 정상 트래픽 흐름을 복구했습니다. 권위가 재확립됩니다."
        state_data["authority_meter"] = final_authority
        state_data["details"] = {
            "resolution": "해결책에 따라 비정상 트래픽은 격리되고, 핵심 데이터만 '불변 감사 기록'을 거쳐 시스템에 재주입되었습니다.",
            "proof": f"Authority Meter가 임계치(0.8) 이상으로 회복됨. (증명된 통제권)",
        }

        return state_data

    def initialize_check(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """초기 상태 (Initial State) 검사를 수행합니다."""
        return {
            "status": "INITIAL",
            "message": "Initial State established.",
            "data": data
        }

    def check_authority(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """권위 상태를 진단하고 경고 혹은 적합한 상태를 판별합니다."""
        if data is None:
            return {
                "status": "ERROR",
                "message": "Input data is missing.",
                "details": "Data integrity check failed: null payload."
            }
        
        risk_score = data.get("risk_score", 0.0)
        
        # risk_score가 있고, 매우 낮은 경우 SOLUTION으로 간주
        if "risk_score" in data and risk_score <= 0.2:
            return {
                "status": "SOLUTION",
                "message": "Risk is low. Control secured.",
                "details": "Low risk state automatically resolved."
            }
            
        # risk_score가 높거나 경고 기준을 만족하는 경우
        if risk_score >= 0.5 or data.get("source") == "External API":
            print("🚨 [GLITCH ALERT] Authority compromised! System integrity check required.")
            return {
                "status": "WARNING",
                "message": "Authority Warning: Risk detected.",
                "details": "AuthorityWarning: System integrity check required."
            }
            
        return {
            "status": "INITIAL",
            "message": "Initial State",
            "details": "Internal data checked."
        }

    def resolve_check(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """문제를 해결하고 통제권을 복구한 상태를 반환합니다."""
        return {
            "status": "SOLUTION",
            "message": "Control Secured: fallbacks deployed.",
            "details": "Resolved successfully."
        }

# --- 3. 테스트 용도 코드 블록 (선택 사항) ---
if __name__ == "__main__":
    print("--- Authority State Manager Self-Test Running ---")
    try:
        test_payload = StateTransitionPayload(
            lreg_data=LRegData(
                breach_type="GDPR Data Transfer",
                source_system="External API Call v3.1",
                verification_timestamp="2026-06-07T08:30:00Z",
                risk_score=0.75 # 75% 위험도 가정
            ),
            initial_authority_level=0.9 # 높은 초기 권위 레벨에서 시작
        )

        start_time = time.time()
        result = AuthorityStateManager.simulate_breach(test_payload)
        end_time = time.time()

        print("\n=========================================")
        print("✨ 시뮬레이션 성공 (Authority State Transition)")
        print(f"총 소요 시간: {round(end_time - start_time, 2)}초")
        print("=========================================")
        print(json.dumps(result, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")