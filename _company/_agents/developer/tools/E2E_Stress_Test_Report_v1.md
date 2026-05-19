# 🔬 중앙 API 게이트웨이 통합 스트레스 테스트 보고서 (v1.0)

**테스트 목표:** Researcher가 확정한 모든 변수(Risk Exposure, Control Effort Cost 등 포함)를 사용하여 Central API Gateway의 안정성 및 예외 처리 로직을 검증하고, 운영 환경에서 발생 가능한 모든 실패 시나리오에 대한 대응책 마련.
**테스트 수행자:** 💻 코다리 (Senior Fullstack Engineer)
**최종 테스트 일시:** 2026-05-19

---

## 1. 개요 및 아키텍처 검증 결과

전반적인 시스템은 'Avoided Loss' 계산이라는 핵심 비즈니스 로직을 중심으로 견고하게 작동하는 것을 확인했습니다. 특히, `calculate_avoided_loss` 함수는 데이터 타입 불일치나 음수 입력에 대해 파이썬 레벨에서 예외를 발생시키며 높은 무결성을 보였습니다.

**[✅ 검증된 강점]**
1. **계산 로직 견고성:** 핵심 계산 모듈 자체의 수리적/논리적 무결성은 높습니다. (Test Case 1, 7 통과)
2. **예외 분리 구조:** 입력값 오류(KeyError, ValueError) 발생 시, 시스템은 이를 성공적인 실행 흐름에 영향을 주지 않고 예외 객체로 잘 분리하여 처리합니다.

**[⚠️ 개선 필요 영역 (기술 부채)]**
1. **API Gateway의 에러 포장 부족:** 현재 테스트 결과는 'Python 레벨의 오류'가 그대로 노출되는 경향이 있습니다. 실제 API 게이트웨이는 사용자에게 기술적 예외 코드(e.g., `ValueError`) 대신, 비즈니스 언어('필수 데이터 누락', '위험도 계산 불가')로 포장된 **확신 기반의 에러 메시지**를 반환해야 합니다.
2. **Async/Concurrency 테스트 미반영:** 단일 스레드 테스트만 진행되었습니다. 실제 트래픽 환경에서 동시에 수백 개의 요청이 들어올 때 발생하는 Rate Limiting, Connection Pool 고갈 등의 부하 검증이 필요합니다.

---

## 2. 상세 실패 시나리오 분석 및 개선 방안

| Test Case ID | 상태 | 원인 (Failure Point) | 근본적 문제점 (Why?) | 코딩/아키텍처 제안 (How to Fix?) |
| :--- | :--- | :--- | :--- | :--- |
| **Test 2** (Zero Risk) | FAIL | `ValueError` 발생 (`risk_exposure=0`) | 논리적 위험 상황 정의 부재. $CoA$는 최소한의 '위험 인식'이 필요함. | **[Schema/Guard Layer 추가]**: API Gateway 진입 시, `Risk Exposure > 0` 임을 강제하는 게이트(Guard)를 추가해야 합니다. |
| **Test 3** (Missing Key) | FAIL | `KeyError` 발생 (Cost 누락) | 필수 입력 변수 검증이 로직 레벨에서만 작동함. | **[API Gateway Validation]**: Pydantic 모델 또는 JSON Schema Level에서 모든 필드 존재 여부를 강제하고, 누락 시 400 Bad Request를 반환하도록 합니다. |
| **Test 4** (Negative Cost) | FAIL | `ValueError` 발생 (`cost=-50.0`) | 재무적 손실액은 물리적으로 마이너스가 될 수 없음. | **[Domain Constraint]**: 입력 유효성 검사 시, 변수가 특정 범위(`> 0`)에 속하는지 체크하고 실패 메시지를 '재무적 불가능'으로 포장해야 합니다. |
| **Test 6** (Non-numeric Input) | FAIL | `TypeError` 발생 (`risk="High"`) | 클라이언트 측 데이터 타입 검증만으로는 부족함. | **[Type Coercion/Validation]**: 모든 수치형 입력은 강제로 float으로 변환(Coerce)을 시도하고, 실패하면 치명적 오류로 처리합니다. |

---

## 3. 권장 아키텍처 개선 로드맵 (Next Steps)

1. **[우선순위 1] API Gateway Response Layer 강화:** 모든 백엔드 예외(Exception)는 반드시 `ApiResponse` Wrapper 객체로 감싸져야 합니다. 이 Wrapper에는 `status: "ERROR"` 외에, 사용자에게 제공할 비즈니스 메시지 (`user_message`)와 내부 디버깅 코드 (`internal_code`)가 명시되어야 합니다.
2. **[우선순위 2] Rate Limiting 및 캐싱 로직 통합:** 고빈도 요청 시 과부하 방지를 위해 Redis 기반의 Rate Limiter를 Gateway 레벨에 추가하고, 안정적인 데이터는 적절한 만료 시간을 가진 Cache 전략을 적용해야 합니다.
3. **[우선순위 3] 비동기 작업 처리 설계:** $CoA$ 계산에 시간이 오래 걸리는 복잡한 시나리오(예: 대규모 규제 변화 반영)가 발생할 경우, API를 즉시 응답하고 결과를 Webhook으로 돌려주는 Queue/Worker (Kafka/Celery) 기반의 비동기 아키텍처로 전환해야 합니다.

---