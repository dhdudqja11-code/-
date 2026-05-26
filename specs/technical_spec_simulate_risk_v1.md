# 🛡️ Mini ROI 리스크 시뮬레이션 API Technical Specification v1.0

**작성일:** 2026-05-26
**버전:** 1.0 (Initial Draft)
**대상 엔드포인트:** `POST /simulate_risk`
**최우선 목표:** 사용자 입력 데이터의 유효성을 검증하고, 리스크 시뮬레이션 결과를 제공함과 동시에, **모든 트랜잭션에 대한 불변 감사 로그(Audit Block)**를 기록하는 것입니다.

---

## 1. 개요 및 비즈니스 요구사항 (Why)

본 엔드포인트는 사용자가 운영하는 시스템 또는 프로젝트가 잠재적으로 노출될 수 있는 리스크 시나리오를 입력받아, 데이터 기반의 재무적/법적 손실액(Loss Amount)을 예측하고 시각화하기 위해 존재합니다.

**핵심 원칙 (The Contract):**
1. **불변성:** 모든 요청은 실패하더라도, 시스템은 해당 트랜잭션이 발생했다는 사실과 그 입력값(`payload`)을 감사 로그에 기록해야 합니다. (Audit Block)
2. **규제 준수:** 계산 공식 및 사용되는 데이터 근거(예: GDPR 위반 시 벌금 상한선 등)는 반드시 외부 참조 문서로 명시되어야 하며, 이 로직은 절대 수정 불가능하게 격리되어야 합니다.

## 2. 엔드포인트 상세 정의 (The How)

### A. 기본 정보
*   **HTTP Method:** `POST`
*   **URI:** `/api/v1/simulate_risk`
*   **요청 본문 (Content-Type):** `application/json`

### B. 요청 데이터 구조 (Request Body / Payload Schema)

모든 필드는 **필수(Required)**하며, 명시된 유효성 검사 규칙을 통과해야 합니다.

| Field Name | Type | Description | Required | Validation Rules |
| :--- | :--- | :--- | :--- | :--- |
| `project_id` | String | 시뮬레이션 대상 프로젝트의 고유 식별자 (UUID). | ✅ Yes | UUID 형식 검증. 존재 여부 확인 필요. |
| `risk_type` | Enum | 분석하고자 하는 리스크 유형. | ✅ Yes | ['DataLeak', 'ComplianceViolation', 'OperationalFailure'] 중 하나여야 함. |
| `operational_period` | String | 시뮬레이션 적용 기간 (YYYY-MM-DD 형식). | ✅ Yes | Date format (ISO 8601). 미래 날짜 불가. |
| `data_volume_gb` | Number | 해당 프로젝트가 보유한 데이터 총량 (GB 단위). | ✅ Yes | Must be >= 0. 실수형(float) 허용. |
| `assumed_failure_rate` | Number | 가정하는 시스템/프로세스의 평균 실패율 (0.0 ~ 1.0). | ✅ Yes | 범위: [0.0, 1.0]. 정규화 필수. |
| `mitigation_cost_annual` | Number | 연간 리스크 완화를 위해 지출된 비용 (예방 투자액). | ❌ No | Must be >= 0. |

### C. 성공 응답 구조 (Success Response Schema)

**Status Code:** `200 OK`
**Description:** 시뮬레이션 계산이 성공적으로 완료되었으며, 결과가 반환됩니다.

```json
{
  "status": "success",
  "simulation_id": "uuid-v4-unique-id", 
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ",
  "input_params": {
    "project_id": "...",
    "risk_type": "ComplianceViolation",
    "operational_period": "2024-12-01",
    // ... 모든 입력값 포함
  },
  "results": {
    "estimated_loss_amount": 150000.00, // 예측 손실액 (통화 단위)
    "roi_score": 0.68,                 // 투자 대비 효과 점수 (0.0 ~ 1.0)
    "required_mitigation_increase": 25000.00 // 권장 추가 예방 비용
  },
  "auditable_log_ref": "audit-uuid-xxxxx" // Audit Block 레코드 참조 ID
}
```

### D. 오류 처리 로직 (Error Handling)

에러는 발생 원인과 다음 조치를 명확히 알려야 합니다. 클라이언트와 서버 에러를 구분합니다.

| Status Code | Error Type | Description | Action Required | Example Payload |
| :--- | :--- | :--- | :--- | :--- |
| `400 Bad Request` | `ValidationError` | 요청 본문(Payload)의 유효성 검증 실패 (e.g., 기간 포맷 오류, 숫자 범위 초과). | Client 측에서 입력값 수정 후 재전송. | `{ "status": "error", "code": 4001, "message": "Invalid date format for operational_period.", "field": "operational_period" }` |
| `403 Forbidden` | `AuthorizationError` | 요청을 보낸 사용자가 해당 프로젝트에 접근할 권한이 없음. | 사용자에게 적절한 권한 부여 필요. | `{ "status": "error", "code": 4032, "message": "Unauthorized access to project_id." }` |
| `500 Internal Error` | `SystemFailure` | 서버 내부 로직 또는 외부 API 호출 중 알 수 없는 오류 발생 (e.g., DB 연결 실패). | Backend 개발팀에 즉시 보고 필요. | `{ "status": "error", "code": 5000, "message": "An unexpected internal error occurred." }` |

## 3. 핵심 로직 흐름 상세: AuditBlock 구현 방안 (The Guardrail)

모든 `POST /simulate_risk` 요청은 다음의 단계별 트랜잭션 구조를 따라야 하며, 이 과정을 **'Audit Block'**으로 정의합니다.

1. **[Phase 1] Request Intake & Validation:**
    *   입력 데이터가 유효한지 검증 (2.B 참고). 실패 시 `400 Bad Request` 반환 및 종료.
2. **[Phase 2] Pre-Execution Audit Log Generation:**
    *   요청이 성공적으로 통과하면, 트랜잭션 시작 시간, 요청자 ID(`auth_user_id`), 그리고 전체 입력값 (`payload`)을 담아 DB의 감사 로그 테이블에 **임시 레코드**를 생성합니다. (실제 계산 전에 '우리가 이 시도(Attempt)를 했다'는 증명).
3. **[Phase 3] Core Calculation:**
    *   `Mini ROI 리스크 계산 로직` 실행. 외부 종속성(예: 최신 법률 데이터베이스 API 호출 등)을 포함할 수 있습니다.
4. **[Phase 4] Transaction Commit & Finalization:**
    *   계산 결과가 성공적으로 도출되면, Phase 2에서 생성된 임시 감사 로그 레코드를 'SUCCESS' 상태로 업데이트하고 최종 결과를 반환합니다. (이것이 `auditable_log_ref`의 출처입니다.)

**⚠️ 중요 검토 사항:**
만약 Phase 3 단계 중 오류가 발생하면, 시스템은 **Phase 2에서 생성된 임시 감사 로그 레코드를 'FAILURE' 상태로 즉시 마킹(Marking)**하고, `500 Internal Error`를 반환해야 합니다. 이 실패 기록까지도 삭제해서는 안 됩니다.