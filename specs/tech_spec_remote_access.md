# 🛠️ 원격 접근 API 핵심 로직 기술 명세서 (Tech Spec v1.0)

## 🎯 개요 및 아키텍처 전제
본 문서는 외부 시스템 또는 내부 에이전트가 '원격으로' 기업의 핵심 데이터/기능에 접근할 때 사용되는 API들의 상세 정의를 포함합니다. 이 로직들은 반드시 다음의 **3단계 강제 게이트웨이 구조**를 거쳐야 합니다.

1.  **Authentication Middleware (`src/middleware/auth.py`):** 사용자 신원 및 기본 권한 검증 (토큰 유효성, 만료 여부).
2.  **Compliance Gateway (`src/gateway/compliance_gateway.py`):** 요청 행위의 합법성 검증. 모든 API 호출이 규제(GDPR, HIPAA 등)에 위배되지 않는지 실시간으로 체크하고, 이 실패 시 즉시 트랜잭션을 중단합니다 (Fail-Fast).
3.  **Core Action Logic:** 실제 비즈니스 로직 실행 및 **Audit Log 생성**.

---

## 🔑 핵심 원격 접근 유닛 3가지 정의 (Endpoints)

### 1️⃣ Endpoint: 민감 데이터 컴플라이언스 검증 보고서 조회
**목적:** 특정 기간/주제에 대한 데이터를 열람하려는 요청을 받지만, 단순 조회로 끝나는 것이 아니라 해당 데이터가 법적으로 사용 가능한 상태인지 **'검증된 증명서(Compliance-Validated Report)'** 형태로만 반환합니다. (Read Only / High Security)

| 항목 | 상세 내용 |
| :--- | :--- |
| **엔드포인트** | `GET /api/v1/reports/validate/{report_id}` |
| **요청 파라미터** | `report_id` (필수, String): 조회하려는 보고서 고유 ID. <br> `start_date`, `end_date` (선택, Date): 데이터 범위 설정. <br> `reason_for_access` (필수, String): 접근 목적 (Audit Log 기록용). |
| **요청 본문** | 없음 |
| **응답 구조 (Success)** | `{ "status": "SUCCESS", "report_id": "R12345", "compliance_score": 98.5, "evidence_summary": "데이터는 [GDPR Art. 6]에 의거하여 접근 가능함.", "data_payload": [...] }` <br> *주의: `data_payload`의 모든 항목에는 **출처(Source)**와 **검증 시점(Verification Time)**이 명시되어야 함.* |
| **응답 구조 (Failure)** | `{ "status": "COMPLIANCE_FAILURE", "error_code": 403, "message": "[문제 정의] 요청된 보고서의 일부 데이터는 현재 규제 위반 소지가 있어 접근 불가.", "mitigation_suggestion": "[해결책 제시] 접근 목적을 '재무적 손실 회피'로 변경하고 관리자 승인을 받으십시오." }` |
| **보안 체크리스트** | ✅ **Scope Check:** 요청된 `report_id`가 사용자의 권한 범위 내에 있는지 확인.<br>✅ **Rate Limiting:** 동일 IP/사용자로부터의 쿼리 빈도를 제한하여 DoS 방지. <br>✅ **Justification Log:** 반드시 `reason_for_access`를 Audit Log에 기록 (누구, 왜 조회했는지). |

---

### 2️⃣ Endpoint: 위험 완화 및 증명 기록 트리거
**목적:** 단순 데이터 수정이 아닌, '위험 상황을 해소하는 조치' 자체를 시스템에 등록하고 실행합니다. 가장 높은 레벨의 트랜잭션으로 간주하며, 실행 즉시 **불변 증명 기록(Audit Log)**을 생성해야 합니다. (Write Action / Critical)

| 항목 | 상세 내용 |
| :--- | :--- |
| **엔드포인트** | `POST /api/v1/actions/trigger_mitigation` |
| **요청 파라미터** | `action_type` (필수, String): 취하려는 위험 유형 (예: '데이터 누락', '권한 오용'). <br> `target_resource_id` (필수, String): 조치 대상 리소스 ID. <br> `mitigation_details` (필수, Object): 구체적인 완화 조치 내용 및 근거 자료 첨부. |
| **요청 본문** | `{ "action_type": "...", "target_resource_id": "...", "mitigation_details": {...} }` |
| **응답 구조 (Success)** | `{ "status": "SUCCESS", "transaction_id": "TXN-98765", "message": "위험 완화 조치가 성공적으로 트리거되었으며, 불변 증명 기록이 생성되었습니다.", "audit_log_url": "/api/v1/logs/txn-98765" }` |
| **응답 구조 (Failure)** | `{ "status": "FAILURE", "error_code": 401, "message": "트랜잭션 실행에 실패했습니다. 이 행위는 최소 2단계의 승인(Two-Factor Auth)이 필요합니다.", "required_action": "관리자 개입 필요" }` |
| **보안 체크리스트** | ✅ **Dual Authorization:** 핵심 트랜잭션은 반드시 사용자 외에 관리자의 별도 인증 (패스워드/OTP)을 요구.<br>✅ **Idempotency Check:** 동일 요청이 여러 번 들어와 시스템 상태를 오염시키는 것을 방지하는 로직 필수. <br>✅ **Async Processing:** 즉시 결과를 반환하기보다, 백그라운드에서 비동기적으로 처리하고 트랜잭션 ID로 상태 추적을 제공해야 함. |

---

### 3️⃣ Endpoint: 사용자 접근 권한 및 규제 위반 시뮬레이터
**목적:** 사용자가 현재 가진 권한으로 어떤 리소스에 얼마나 깊이 접근할 수 있는지, 그리고 그 과정에서 발생 가능한 법적 위험을 사전에 시뮬레이션하고 보고서로 제공합니다. (Simulation & Read Only)

| 항목 | 상세 내용 |
| :--- | :--- |
| **엔드포인트** | `GET /api/v1/user/simulate_risk` |
| **요청 파라미터** | `target_context` (필수, String): 시뮬레이션 대상 컨텍스트 (예: 'HIPAA 데이터', 'GDPR 개인정보'). <br> `hypothetical_action` (필수, String): 가상의 행동 시나리오 (예: '데이터를 제3자에게 전송'). |
| **요청 본문** | 없음 |
| **응답 구조 (Success)** | `{ "status": "SIMULATION_REPORT", "context": "HIPAA", "risk_level": "CRITICAL", "potential_loss_usd": 250000, "violation_details": ["GDPR Article 17 위반"], "mitigation_steps": ["익명화 처리 필수", "별도 동의 확보"] }` |
| **응답 구조 (Failure)** | `{ "status": "ERROR", "message": "시뮬레이션 로직 실행에 실패했습니다. 내부 시스템 상태를 점검하십시오." }` |
| **보안 체크리스트** | ✅ **Input Sanitization:** `target_context`와 `hypothetical_action` 파라미터에 대한 XSS 및 Injection 공격 방어 필수.<br>✅ **Isolation:** 이 로직은 실제 데이터베이스의 쓰기 작업을 수행해서는 안 되며, 반드시 격리된(Sandbox) 환경에서만 실행되어야 함. <br>✅ **Transparency:** 모든 시뮬레이션 결과에는 계산에 사용된 가중치와 공식이 명시되어 신뢰도를 높여야 함 (블랙박스 금지). |

---
**요약 및 기술적 주해:**
이 3가지 엔드포인트는 단순 API가 아니라, **'컴플라이언스를 통과하는 게이트웨이 역할을 수행하는 비즈니스 로직 레이어'**입니다. 특히 응답 실패 케이스(Failure Response)를 설계할 때, 단순히 에러 코드만 반환할 것이 아니라 반드시 위에서 정의한 [문제 정의 → 원인 분석 → 해결책 제시] 3단계 구조를 따르도록 강제해야 합니다.