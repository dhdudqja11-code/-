import json
from typing import Dict, Any, Tuple
# from fastapi import APIRouter # 실제 환경에서는 라우터 사용 예정

# --- 1. State Definitions and Constants ---
class AuthorityState:
    IDLE = "IDLE"        # 초기 상태: 모든 것이 정상적임 (초기 전제)
    WARNING = "WARNING"  # 경고 상태: 리스크 임계치 초과, 통제가 필요함
    CONTROLLED = "CONTROLLED" # 통제 완료 상태: 문제 진단 및 해결책 제시를 통해 권위 재확립

def calculate_authority_score(lreg_metrics: Dict[str, float]) -> Tuple[float, str]:
    """
    Authority Score를 계산하고 시스템의 현재 State를 결정합니다.
    핵심 원칙: 최약점 원칙 (Weakest Link Principle)을 적용하여 가장 낮은 점수가 전체 Authority에 영향을 줍니다.
    :param lreg_metrics: M1(Cross-Border), M2(Audit Trail), M3(Bias Deviation)의 현재 측정값.
    :return: (Authority Score, State String)
    """

    # 1. 가중치 정의 및 입력 유효성 검사 (Guard Clause)
    weights = {
        "M1_Viability": 0.4,  # 데이터 국경 이동 안정성 (가장 중요도가 높음 가정)
        "M2_Completeness": 0.3, # 법적 책임 증명 (무결성이 생명)
        "M3_Deviation": 0.3   # AI 규제 리스크 (미래 대비)
    }

    authority_scores = {}
    for metric, weight in weights.items():
        try:
            # M1, M2는 높은 값이 좋고(Score), M3는 낮은 값이 좋은(Deviation Rate) 경향성을 반영하여 스코어링합니다.
            if "Viability" in metric or "Completeness" in metric:
                score = lreg_metrics.get(metric.split('_')[-1], 0.0) * 100 # 최대 100점 기준
            else: # M3 (Deviation Rate)는 역산하여 점수화 (e.g., 0.1 -> 90점)
                raw_rate = lreg_metrics.get(metric.split('_')[-1], 1.0)
                score = max(0, min(100, 1 - raw_rate)) * 100 # 최대 100점 기준

            authority_scores[metric] = score * weight
        except KeyError:
            # 데이터 누락 시, 해당 지표의 기여도를 0으로 처리하여 시스템이 무너지지 않게 함. (Authority Principle)
            print(f"Warning: Missing metric data for {metric}. Assuming contribution of 0.")
            authority_scores[metric] = 0.0

    # 2. Authority Score 계산 (가중치 합산)
    total_score = sum(authority_scores.values())

    # 3. State Transition Logic 구현 (Thresholding & Authority Check)
    if total_score >= 85:
        state = AuthorityState.CONTROLLED # 통제권 확보 완료: 높은 점수, 시스템이 권위를 잡음
        message = "시스템적 통제권 확보 완료. 모든 핵심 지표가 임계치를 상회하여 안전합니다."
    elif total_score >= 60:
        state = AuthorityState.WARNING # 경고 상태: 일부 리스크 발생, 즉각적인 조치가 필요함
        message = "주의: 특정 $L_{reg}$ 지표에서 위험 신호가 감지되었습니다. 시스템의 통제권 확보 과정이 필요합니다."
    else:
        state = AuthorityState.IDLE # 초기/최저점 상태: (실제로는 이보다 더 낮은 점수가 나와야 하지만, 최소한의 기본값 설정)
        message = "시스템 모니터링 중. 데이터를 통해 리스크 패턴을 분석하고 있습니다."

    return round(total_score, 2), state, message


def analyze_authority_state(lreg_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Authority Meter의 모든 로직을 감싸는 메인 진입점 함수.
    API Gateway Level에서 호출될 것을 가정합니다.
    """
    score, state, message = calculate_authority_score(lreg_data)

    # Authority Warning 구조를 포함하여 응답하는 것이 핵심입니다. [근거: 💻 코다리 — 검증된 지식]
    response = {
        "status": "success",
        "state": state, # IDLE, WARNING, CONTROLLED 중 하나
        "authority_score": score,
        "message": message,
        "lreg_details": lreg_data
    }

    # 상태에 따른 추가적인 권위 메시지 첨부 (시스템적 통제감 강조)
    if state == AuthorityState.WARNING:
         response["warning_alert"] = "🚨 [CRITICAL] 시스템 데이터 무결성 검사 필요! 즉시 $L_{reg}$ 점검 절차를 시작하십시오."
    elif state == AuthorityState.CONTROLLED:
        response["success_confirmation"] = "✅ [AUTHORITY GAINED] 통제권 재확립 성공. 다음 단계는 리스크 제거가 아닌, 기회 포착입니다."

    return response

# --- 2. Dummy API Endpoint Simulation (FastAPI context) ---
async def simulate_api_call(data: Dict[str, float]) -> dict:
    """
    실제 외부 API 호출을 시뮬레이션하는 더미 함수.
    이것이 프론트엔드에서 fetch()로 호출될 지점입니다. [근거: 💻 코다리 — 검증된 지식]
    """
    print(f"--- Simulating API call with data: {data} ---")
    return analyze_authority_state(data)

# 테스트용 데이터 예시 (Development/QA 환경에서 활용)
DUMMY_HIGH_RISK_DATA = {"Viability": 0.6, "Completeness": 0.95, "DeviationRate": 0.2} # M1 낮음 -> WARNING 유도
DUMMY_LOW_RISK_DATA = {"Viability": 0.9, "Completeness": 0.98, "DeviationRate": 0.05}  # 전반적으로 높음 -> CONTROLLED 유도

if __name__ == "__main__":
    print("="*50)
    print("--- 테스트 케이스 1: WARNING 상태 시뮬레이션 ---")
    warning_result = simulate_api_call(DUMMY_HIGH_RISK_DATA)
    print(json.dumps(warning_result, indent=2))

    print("\n" + "="*50)
    print("--- 테스트 케이스 2: CONTROLLED 상태 시뮬레이션 ---")
    controlled_result = simulate_api_call(DUMMY_LOW_RISK_DATA)
    print(json.dumps(controlled_result, indent=2))

# 이 파일은 E2E 데모의 핵심 백엔드 로직입니다. 반드시 타입 안전성 검증이 필요합니다.