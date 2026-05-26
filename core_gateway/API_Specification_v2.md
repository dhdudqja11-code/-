# 🛡️ Immutable Audit Gateway (IAG) API 명세서 v2.0: 원격 제어 프로그램 연동
> **목표:** 모든 Mini ROI 시뮬레이션 기반의 핵심 비즈니스 로직 호출은 이 게이트웨이를 단일 진입점(SSoT)으로 거쳐야 하며, 법적 무결성을 증명하는 `AuditBlock` 생성이 강제된다.

## 1. 인증 및 인가 흐름 (Authentication & Authorization)
*   **전송 방식:** 모든 API 요청은 HTTPS를 통해 전송되어야 한다.
*   **인증(AuthN):** **JWT Bearer Token (RS256)**을 HTTP Header (`Authorization: Bearer <token>`)에 포함해야 한다. 토큰 만료 시간(exp) 및 발급자(iss) 검증이 필수다.
*   **인가(AuthZ):** JWT Payload 내의 `roles` 클레임을 분석하여, 요청된 기능(`endpoint`) 수행 권한을 체크한다. (예: `ROLE_ADMIN`만 특정 리스크 시뮬레이션 호출 가능).

## 2. API 엔드포인트 정의
| Endpoint | Method | Description | 요구되는 AuthZ | 데이터 흐름 |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/simulate_risk` | POST | Mini ROI 시뮬레이션 실행 및 리스크 점수 산출. **(핵심 트랜잭션 진입점)** | `ROLE_USER`, `ROLE_ADMIN` | Request Body: `{ "user_id": str, "data_source": dict }` |
| `/api/v1/check_compliance` | POST | 외부 규제 데이터와 내부 트랜잭션 데이터를 비교하여 위험 경고 생성. **(핵심 트랜잭션 진입점)** | `ROLE_USER`, `ROLE_ADMIN` | Request Body: `{ "transaction_id": str, "timestamp": int }` |
| `/api/v1/status` | GET | 시스템 상태 및 최근 감사 로그 조회 (읽기 전용). | `ROLE_GUEST` | Header Only |

## 3. 핵심 데이터 구조: AuditBlock 강제화
모든 성공(2xx) 또는 실패(4xx, 5xx) 응답은 이 표준 구조를 반드시 따라야 한다. 시스템이 어떤 상태였는지에 대한 불변의 증거가 되어야 하므로 절대 생략 불가하다.

```json
{
  "status": "SUCCESS" | "FAILURE",
  "timestamp_utc": "2026-05-26T10:00:00Z",
  "transaction_id": "uuid-generated-by-server",
  "audit_details": {
    "source_api": "/api/v1/simulate_risk",
    "initiator_user_id": "user-abc-123",
    "requested_action": "Mini ROI Simulation",
    "result_summary": "High Risk detected in Data Source A.",
    "audit_payload": { 
      // 실제 비즈니스 로직의 결과가 들어가는 곳 (예: MiniROIResult)
      "mini_roi_score": 0.85,
      "detected_risks": ["Data Integrity Breach", "Regulatory Non-Compliance"]
    }
  },
  "message": "Transaction processed successfully." | "Error occurred during processing."
}
```

## 4. 실시간 스트리밍 처리 고려 사항 (Streaming Consideration)
*   **요구사항:** Mini ROI 시뮬레이션의 결과가 복잡하고 계산 시간이 길 경우, 클라이언트에게 즉각적인 피드백이 필요하다.
*   **기술 스택:** WebSocket 또는 Server-Sent Events (SSE)를 사용하여 스트리밍 방식을 채택한다.
*   **처리 흐름:** 요청 수신 $\rightarrow$ 초기 인증/인가 통과 $\rightarrow$ Worker Queue(Redis/Celery 등)에 작업 할당 $\rightarrow$ 계산 진행 상황을 주기적으로 클라이언트에게 `AuditBlock` 형태로 전송. (완료 시 최종 AuditBlock 전달).

---