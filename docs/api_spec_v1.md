# 🌐 마음을 묻다 - 시스템 통합 API 사양서 (API Gateway Level)

## 개요: The Content Architect Engine v2
본 사양서는 '마음을 묻다' 서비스의 모든 백엔드 로직 및 데이터 파이프라인을 통합하는 단일 진입점(Single Entry Point)인 **API Gateway**를 중심으로 합니다. 외부 개발자는 이 API 게이트웨이를 통해서만 모든 기능에 접근해야 하며, 이는 시스템의 권위와 통제력을 보장합니다.

### 🚀 핵심 원칙 (Must-Haves)
1.  **모든 요청은 구조화되어야 함:** 모든 입력 및 출력 데이터는 **JSON Schema**를 따르며, 단순 문자열 반환을 금지합니다 [근거: 💻 코다리 — 검증된 지식].
2.  **실패 흐름의 권위적 정의:** 에러 메시지는 단순히 HTTP Status Code로 끝나는 것이 아니라, 시스템이 문제를 진단하고 해결책을 제시하는 'Authority Warning' 구조를 갖춰야 합니다 [근거: 🏢 회사 정체성].
3.  **추적 가능성(Traceability):** 모든 데이터 조회 및 분석 결과는 반드시 **데이터 출처(Source)**와 **검증 시점(Verification Time)** 메타데이터를 포함해야 합니다.

---

## I. API Gateway Endpoints (FastAPI 기반 가정)

| 엔드포인트 | HTTP Method | 목적 | 인증/권한 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| `/auth/token` | `POST` | JWT 토큰 발급 및 사용자 식별. | Public | 필수 전처리 단계. |
| `/risk/check` | `GET` | 특정 주체(트랜잭션)의 법적 리스크 진단 (핵심). | User Token | **Authority Warning 로직 호출 지점.** |
| `/execute-command` | `POST` | 원격 환경에서 명령어 실행 및 데이터 스트리밍. | High Privilege | 시스템 통제권 재확립 시뮬레이션. |
| `/generate-content` | `POST` | 콘텐츠 청사진 생성 (기존 기능 유지). | User Token | LLM 호출 플로우 (Step 1~4) 포함. |

---

## II. 핵심 엔드포인트 상세 사양: GET /risk/check

이 엔드포인트는 서비스의 권위를 상징하는 가장 중요한 부분입니다. 외부 트랜잭션 데이터와 법적 리스크 DB를 결합하여 진단합니다.

### ✅ Request Body (Query Parameters)
*   `transaction_id`: 조회할 가상의 트랜잭션 ID (String).
*   `source_system`: 데이터를 발생시킨 시스템 출처 (Enum: `PaymentGateway`, `UserInput`, `APIWebhook`).
*   `time_range`: 분석할 시간 범위 (`start_date` / `end_date`).

### 💡 Success Response Body (200 OK)
```json
{
  "status": "SUCCESS",
  "diagnosis": {
    "risk_score": 0.85, // 0.0 ~ 1.0 사이의 정량화된 리스크 점수
    "alert_level": "HIGH_CRITICAL",
    "summary": "트랜잭션 A는 [법규 조항 XXX] 위반 가능성이 높습니다."
  },
  "analysis_details": {
    "vulnerability_found": true,
    "legal_violation": {
      "statute_code": "GlobalReg-Art4.2",
      "description": "데이터의 출처와 검증 시점을 명확히 하지 않았습니다.",
      "financial_impact_usd": 15000 // 재무적 영향 정량화 필수
    }
  },
  "metadata": {
    "data_source": "Global Regulatory Database",
    "verification_time": "2026-06-03T14:30:00Z"
  }
}
```

### ⚠️ Failure/Error Response Body (Authority Warning Flow)
API Gateway는 단순 에러 코드 대신, 이 표준화된 경고 메시지를 반환해야 합니다. 이는 시스템의 권위를 유지하는 핵심 로직입니다.

```json
{
  "status": "AUTHORITY_WARNING",
  "error_code": "E403_DATA_INTEGRITY",
  "message": "시스템적 통제권 재확립 중: 데이터 무결성 검사 실패.",
  "warning_details": {
    "problem_definition": "요청된 트랜잭션의 [Source/Time] 메타데이터가 DB와 불일치합니다. (What went wrong?)",
    "root_cause_analysis": "외부 데이터 요청 시, 필요한 '추적 가능성' 필드(Traceability Field)가 누락되었습니다. (Why did it go wrong?)",
    "mitigation_suggestion": [
      "1. 트랜잭션 발생 시스템에서 Source/Time 메타데이터를 필수 전송하도록 수정하십시오.",
      "2. 백엔드 게이트웨이 레벨에서 Input Validation을 강화해야 합니다."
    ]
  },
  "metadata": {
    "gateway_log_id": "AUTH-20260603-A1B2C3D4",
    "timestamp": "2026-06-03T14:35:00Z"
  }
}
```

---

## III. QA 체크리스트 (QA Checklist for External Developers)

외부 개발자가 이 API를 연동할 때 반드시 테스트해야 할 필수 기능 및 실패 경로입니다.

### 🟢 Positive Flow Test Cases (성공 흐름 검증)
1. **[T-001] 정상 리스크 진단:** 유효한 트랜잭션 데이터(Source, Time 포함)로 요청 시, `risk_score`와 `analysis_details`가 정확히 반환되는지 확인한다.
2. **[T-002] 성공 메타데이터 검증:** 응답 JSON의 `metadata` 섹션에 `data_source` 및 `verification_time`이 포함되어 신뢰성을 확보하는지 확인한다.

### 🔴 Negative Flow Test Cases (권위적 경고 로직 검증)
1. **[T-003] 데이터 무결성 실패:** Source/Time 메타데이터가 누락되거나, DB와 불일치할 때 `200 OK` 대신 `AUTHORITY_WARNING` 상태 코드를 반환하는지 확인한다. (Critical Path).
2. **[T-004] 권한 부족(Access Denied):** 유효하지 않거나 낮은 권한의 토큰으로 요청했을 때, 시스템이 패닉 없이 전문적인 에러 코드와 함께 '통제권 재확립 중...' 메시지를 출력하는지 확인한다.
3. **[T-005] API 호출 과부하(Rate Limit):** 정의된 트래픽 제한을 초과할 경우, 단순 `429 Too Many Requests`가 아닌, 시스템의 안정성을 강조하는 권위적 경고와 함께 재시도 가이드라인을 제공하는지 확인한다.