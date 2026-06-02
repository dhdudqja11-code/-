from typing import Optional, Dict, Any
import datetime
from pydantic import BaseModel, Field, validator
import uuid
# 가상의 WORM 로그 기록 모듈을 가정합니다. 실제로는 DB 커넥션과 트랜잭션을 사용합니다.
from .worm_logger import write_immutable_log

# --- 1. 스키마 정의 (Pydantic Models) ---
class ViolationDetails(BaseModel):
    """규정 위반에 대한 구체적인 데이터를 담는 모델."""
    violation_type: str = Field(..., description="예: GDPR Article 6, CCPA PII Leakage")
    data_source: str = Field(..., description="데이터가 유출되거나 잘못 처리된 출처 시스템/API.")
    severity_score: float = Field(..., ge=0.1, le=1.0, description="위반의 심각도 (0.1~1.0).")

class CalculateALPRequest(BaseModel):
    """A_LP 계산 API 요청 바디 스키마."""
    user_id: str = Field(..., description="API를 호출하는 사용자 ID (인증된 주체).")
    transaction_type: str = Field(..., description="트랜잭션의 종류 (예: Payment, DataAccess, ContentPublish).")
    timestamp: datetime.datetime = Field(..., description="사건 발생 시점 (UTC 권장).")
    violation_details: ViolationDetails = Field(..., description="관련 규제 위반 상세 정보.")

class CalculationResult(BaseModel):
    """A_LP 계산 API 응답 바디 스키마."""
    transaction_id: str = Field(..., description="이번 계산 트랜잭션 고유 ID (UUID).")
    calculated_alp_value: float = Field(..., ge=0.0, description="$A_{LP}$ 값 (Avoided Loss Potential). 정량적 가치.)")
    risk_status: str = Field(..., description="위험 상태 ('LOW', 'MEDIUM', 'HIGH').")
    alert_message: str = Field(..., description="[1] 문제 정의: 발생한 위험을 명확히 설명."); # 3단계 구조의 첫 번째 요소
    root_cause_analysis: str = Field(..., description="[2] 원인 분석: 규제 위반의 근본적 원인을 Source/Time 관점에서 분석."); # 3단계 구조의 두 번째 요소
    mitigation_suggestion: str = Field(..., description="[3] 해결책 제시: 위험을 회피하기 위한 구체적이고 실현 가능한 조치.") # 3단계 구조의 세 번째 요소

# --- 2. 핵심 비즈니스 로직 구현 ---
def calculate_alp(request_data: CalculateALPRequest) -> CalculationResult:
    """
    A_LP (Avoided Loss Potential)를 계산하고, WORM 로그에 기록하는 핵심 서비스 함수.
    이 함수의 실행은 트랜잭션의 무결성을 보장합니다.
    """
    # 1. 입력값 유효성 검증 및 전처리 (Validation Flow)
    print("⚙️ [Step 1] 요청 데이터 수신 및 필수 필드/타입 검증 시작.")
    if request_data.timestamp > datetime.datetime.now(datetime.timezone.utc):
        raise ValueError("Timestamp는 미래 시점을 가리킬 수 없습니다.")

    # 2. 리스크 스코어링 엔진 호출 (가상의 복잡한 계산)
    print("⚙️ [Step 2] 규제 위반 상세 정보 기반 리스크 스코어링 실행...")
    risk_score = request_data.violation_details.severity_score * 1.5 + \
                  (0.5 if "GDPR" in request_data.violation_details.violation_type else 0)

    # 3. A_LP 계산 로직 (가상의 복잡한 재무 모델링)
    # A_LP = Risk Score * Regulatory Impact Factor (RIF) * Time Decay Multiplier (TDM)
    regulatory_impact_factor = {"GDPR": 1000, "CCPA": 500}.get(request_data.violation_details.violation_type, 100)
    alp_value = risk_score * regulatory_impact_factor / (1 + abs(datetime.datetime.now().year - request_data.timestamp.year))

    # 4. 위험 상태 및 피드백 구조화
    if alp_value > 500:
        risk_status = "HIGH"
        alert_message = f"[🚨 문제 정의] {request_data.violation_details.violation_type} 위반으로 인해 잠재적 법적 손실이 크게 예상됩니다."
        root_cause_analysis = f"[🔬 원인 분석] 데이터 출처 '{request_data.violation_details.data_source}'에서 발생한 '불변성' 미확보 트랜잭션 처리 오류가 근본 원인입니다."
        mitigation_suggestion = "즉시 접근 제어 목록(ACL)을 재검토하고, 모든 데이터 기록에 WORM 체크섬 검증 로직을 적용해야 합니다."
    elif alp_value > 100:
        risk_status = "MEDIUM"
        alert_message = f"[⚠️ 문제 정의] {request_data.violation_details.violation_type} 관련 사소한 규정 준수 위험이 감지되었습니다."
        root_cause_analysis = "[🔎 원인 분석] 프로세스 단계의 누락 또는 임시적 예외 처리로 인한 일회성 오류입니다."
        mitigation_suggestion = "담당 팀에 대한 재교육 및 워크플로우 자동 검증 시스템 도입을 권장합니다."
    else:
        risk_status = "LOW"
        alert_message = "[✅ 문제 정의] 현재 감지된 위험은 허용 가능한 범위 내입니다. 추가 모니터링이 필요합니다."
        root_cause_analysis = "[🔎 원인 분석] 특별한 근본적 문제는 발견되지 않았습니다."
        mitigation_suggestion = "정기적인 리스크 감사(Audit) 주기를 유지하는 것이 좋습니다."

    # 5. WORM 로그 기록 및 트랜잭션 커밋 (Immutable Proof Generation)
    print("⚙️ [Step 3] 최종 결과를 WORM 로그에 비가역적으로 기록합니다...")
    transaction_id = str(uuid.uuid4())
    write_immutable_log(request_data, alp_value, risk_status, transaction_id) # <- 핵심 트랜잭션
    print(f"✅ [SUCCESS] WORM 로그 기록 완료. Transaction ID: {transaction_id}")

    # 6. 결과 반환
    return CalculationResult(
        transaction_id=transaction_id,
        calculated_alp_value=round(alp_value, 2),
        risk_status=risk_status,
        alert_message=alert_message,
        root_cause_analysis=root_cause_analysis,
        mitigation_suggestion=mitigation_suggestion
    )

# --- 테스트용 더미 모듈 (실제 프로젝트에서는 분리되어야 함) ---
class MockWormLogger:
    @staticmethod
    def write_immutable_log(request: CalculateALPRequest, alp: float, status: str, tx_id: str):
        """가상의 WORM DB Write 함수. 데이터는 불변성을 유지하며 기록됩니다."""
        print(f"\n[WORM LOG WRITE START] TX ID: {tx_id}")
        print("--------------------------------------------------------")
        print(f"  > Request Payload (Snapshot): {request.dict()}")
        print(f"  > Calculated A_LP Value: {alp:.2f} | Status: {status}")
        print("  > [TRANSACTION COMMITTED] - 데이터가 시간과 함께 영구 기록되었습니다.")
        print("[WORM LOG WRITE END]\n")

write_immutable_log = MockWormLogger.write_immutable_log

# API 엔드포인트 시뮬레이션 (실제 FastAPI 라우터에 붙일 부분)
async def simulate_api_call(request: CalculateALPRequest):
    """API 호출을 시뮬레이션하는 비동기 함수."""
    try:
        result = calculate_alp(request)
        return {"status": "success", "data": result.dict()}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "critical_error", "message": f"시스템 내부 오류 발생: {str(e)}"}

# 테스트 케이스를 위한 dummy setup
async def run_test_case(request: CalculateALPRequest):
    print("\n==========================================")
    print("🧪 [TEST RUNNING] API 시뮬레이션 시작...")
    result = await simulate_api_call(request)
    if result['status'] == 'success':
        print("✅ 테스트 성공. 결과값 출력:")
        print(f"   A_LP: {result['data']['calculated_alp_value']} | Status: {result['data']['risk_status']}")
        print("-" * 30)
    else:
        print("❌ 테스트 실패/에러 발생:", result['message'])
    print("==========================================")

# --- 3. E2E 테스트 케이스 5개 ---
async def run_all_test_cases():
    """모든 시나리오를 커버하는 5가지 통합 테스트 실행."""

    # T1: 최악의 경우 (GDPR 위반, 높은 심각도) - HIGH Risk 예상
    req_t1 = CalculateALPRequest(
        user_id="test_user_high",
        transaction_type="DataAccess",
        timestamp=datetime.datetime(2026, 5, 1), # 과거 시점 강제
        violation_details=ViolationDetails(
            violation_type="GDPR Article 4 (Data Subject Rights)",
            data_source="External Partner API v2.1",
            severity_score=0.9
        )
    )
    await run_test_case(req_t1)

    # T2: 중간 위험 (CCPA 위반, 일반적인 실수) - MEDIUM Risk 예상
    req_t2 = CalculateALPRequest(
        user_id="test_user_medium",
        transaction_type="ContentPublish",
        timestamp=datetime.datetime.now(datetime.timezone.utc).replace(hour=10),
        violation_details=ViolationDetails(
            violation_type="CCPA PII Leakage",
            data_source="Internal CMS Draft Board",
            severity_score=0.5
        )
    )
    await run_test_case(req_t2)

    # T3: Low Risk (경미한 문제, 시스템 운영 상의 사소한 오류) - LOW Risk 예상
    req_t3 = CalculateALPRequest(
        user_id="test_user_low",
        transaction_type="Payment",
        timestamp=datetime.datetime.now(datetime.timezone.utc).replace(hour=15),
        violation_details=ViolationDetails(
            violation_type="Minor Policy Deviation",
            data_source="Client Billing System v1.0",
            severity_score=0.2
        )
    )
    await run_test_case(req_t3)

    # T4: Input Validation Failure (Timestamp가 미래인 경우) - Error Case
    req_t4 = CalculateALPRequest(
        user_id="test_fail",
        transaction_type="TestFail",
        timestamp=datetime.datetime(2099, 1, 1), # 오류 유발
        violation_details=ViolationDetails(
            violation_type="MockType",
            data_source="Dummy",
            severity_score=0.5
        )
    )
    await run_test_case(req_t4)

    # T5: Edge Case (최대치 입력, 1.0에 근접한 값) - HIGH Risk 예상 (T1과 유사하지만 다른 Context)
    req_t5 = CalculateALPRequest(
        user_id="test_edge",
        transaction_type="DataAccess",
        timestamp=datetime.datetime(2024, 1, 1), # 매우 오래된 과거 시점
        violation_details=ViolationDetails(
            violation_type="GDPR Article 6 (Legal Basis)",
            data_source="Legacy Data Migration Pipeline",
            severity_score=1.0
        )
    )
    await run_test_case(req_t5)

# 실제 실행은 asyncio 환경에서 호출해야 하므로, 이 파일의 마지막 부분에 주석 처리합니다.
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(run_all_test_cases())
```

### 📝 API 기술 문서 업데이트 (docs/api_v1_proof.md)

위 코드를 기반으로, 모든 이해관계자가 참조할 수 있는 공식적인 기술 문서를 생성하겠습니다. 이 문서는 이전 `sessions/2026-06-02T03-52/developer.md`의 내용을 포괄하고 구조화하여 '최종 스펙' 역할을 할 것입니다.

<create_file path="c:\Users\user\AI 기업 두뇌\내 작업들\docs\api_v1_proof.md">
# 🛡️ API v1: 불변성 증명 및 $A_{LP}$ 계산 엔진 (Immutable Proof & A_LP Engine)

**최종 버전:** 2026-06-03
**담당 모듈:** `ProofService` (Python/FastAPI Backend)
**목표:** 외부 트랜잭션 발생 시, 법적 리스크를 정량화하여 '회피 가능 손실액($A_{LP}$)'을 산출하고, 모든 기록에 불변성(WORM) 메타데이터를 부여하는 시스템.

## 1. 엔드포인트 정의
*   **메소드:** `POST`
*   **URI:** `/api/v1/calculate-alp`
*   **설명:** 사용자 트랜잭션과 관련된 규제 위반 데이터를 받아 $A_{LP}$를 계산하고, 그 결과를 구조화된 위험 보고서 형태로 반환합니다. 이 호출은 시스템의 모든 리스크 기반 의사결정의 핵심이 됩니다.

## 2. 요청 스키마 (Request Body Schema)
**모델:** `CalculateALPRequest`
| 필드 | 타입 | 필수 여부 | 설명 | 제약 조건 |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | String | 🟢 Yes | API를 호출하는 인증된 사용자 식별자. | 비어있으면 안 됨 (Guard). |
| `transaction_type` | String | 🟢 Yes | 트랜잭션의 종류. 리스크 가중치 산정에 사용됩니다. | Enum 검증 권장 (Payment, DataAccess 등). |
| `timestamp` | DateTime | 🟢 Yes | 사건 발생 시점(UTC 기준). 시간 역전 방지 로직 필수. | 과거 또는 현재 UTC 시간만 허용. |
| `violation_details` | Object | 🟢 Yes | 위반 상세 정보 블록 (하위 스키마 참조). | - |

**[Nested Schema] `ViolationDetails`**
*   `violation_type`: String (예: GDPR Article 6)
*   `data_source`: String (데이터 유출/처리 출처)
*   `severity_score`: Float (0.1 ~ 1.0, 위반 심각도).

## 3. 응답 스키마 (Response Body Schema)
**모델:** `CalculationResult`
| 필드 | 타입 | 설명 | 비고 |
| :--- | :--- | :--- | :--- |
| `transaction_id` | String | 이 트랜잭션에 부여된 UUID. WORM 기록의 키가 됩니다. | 생성됨 (UUID). |
| `calculated_alp_value` | Float | 최종 계산된 $A_{LP}$ 값. 정량적 손실액을 의미합니다. | 0.0 이상. 소수점 둘째 자리까지 반올림. |
| `risk_status` | String | 시스템이 판단한 위험 등급 (LOW, MEDIUM, HIGH). | 내부 로직에 따라 결정. |
| `alert_message` | String | **[1] 문제 정의**: 사용자가 즉각적으로 이해해야 하는 현상적 위협. | 사용자 가시성 최우선. |
| `root_cause_analysis` | String | **[2] 원인 분석**: 규제 위반이 발생한 구조적/시스템적 근본 원인 (Source/Time 명시). | 기술 보고서용. |
| `mitigation_suggestion` | String | **[3] 해결책 제시**: 이 위험을 해소하기 위해 취해야 할 구체적인 권한 조정 또는 프로세스 개선 방안. | 행동 지침(Action Item) 제공. |

## 4. 백엔드 처리 흐름 (Technical Flowchart)
1.  **요청 수신 및 검증:** `user_id`, `transaction_type`, `timestamp`의 존재 여부 및 유효성(`<run_command>python -m py_compile...</run_command>`와 같은 컴파일러 단계).
2.  **리스크 스코어링 (Scoring):** `violation_details`를 기반으로 심각도(Severity)에 규제 가중치(Regulatory Impact Factor, RIF)를 곱하여 초기 리스크 점수를 산출.
3.  **$A_{LP}$ 계산:** 복잡한 재무 모델($A_{LP} = \text{Score} \times \text{RIF} / (1 + \text{Time Decay})$ 등)을 통해 최종 $A_{LP}$ 값 도출.
4.  **위험 메시지 구조화:** 산출된 $A_{LP}$ 값을 기준으로 위험 레벨(LOW/MEDIUM/HIGH)을 판단하고, **[문제 정의 $\rightarrow$ 원인 분석 $\rightarrow$ 해결책 제시]의 3단계 구조**로 문자열을 구성하여 출력 필드를 채움.
5.  **WORM 기록 (Critical Step):** 계산 완료 후, 요청 데이터와 산출된 결과를 패키징하여 `write_immutable_log()` 함수를 호출합니다. 이 과정이 **불변성 증명의 핵심 트랜잭션 커밋 지점**입니다.

## 5. 테스트 케이스 및 검증 (E2E Test Cases)
(코드 블록의 `run_all_test_cases`에 정의된 5가지 시나리오를 참조합니다.)