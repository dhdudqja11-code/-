# 마음을 묻다 - 시스템 통합 API 사양서 (Authority Gateway v2.0)
## 개요
본 문서는 '마음을 묻다' 서비스의 모든 백엔드 로직 및 데이터 파이프라인을 통합하는 단일 진입점(Single Entry Point)인 **API Gateway**를 중심으로 합니다. 외부 개발자는 이 API 게이트웨이를 통해서만 모든 기능에 접근해야 하며, 이는 시스템의 권위와 통제력을 보장합니다.

## 핵심 스키마: AuthorityCheckResponseSchema
[여기에 위에서 정의한 JSON Schema 전체 내용을 삽입]

### 1. 상태 전이 플로우 (State Transition Flow)
모든 응답은 다음 세 가지 흐름 중 하나를 따릅니다.
1. **성공 (SUCCESS):** 모든 지표가 정상 범위 내에 있을 때. 시스템 권위 점수(Authority Score) 제시.
2. **경고 (WARNING):** 잠재적 위험이 감지되었으나 통제 가능할 때. `authority_warning`과 함께 즉각적인 해결책(`resolution_plan`)을 강제 제시.
3. **오류 (ERROR):** 시스템 자체의 치명적인 오류 발생 시. 사용자에게 패닉 대신 '통제권 재확립' 메시지를 제공하고, 복구 프로토콜(`recovery_protocol`) 실행.

### 2. 데이터 변수 매핑 ($L_{reg}$ Metrics)
*   **$V_1$: JurisdictionChangeDetected:** (Type: Boolean) 규정 위반 감지 여부 (Trigger).
*   **$V_2$: DataResidencyViolation:** (Type: Object) 위반 범위, 발생 지점, 영향받는 데이터 유형.

### 3. API 엔드포인트 및 테스트 케이스
- **Endpoint:** POST /api/v1/check_authority
- **Request Body:** { "user_id": string, "data_set_id": string, ... }
- **Test Cases (Mandatory):**
    *   T-001: Normal Operation (SUCCESS)
    *   T-002: Compliance Warning Triggered (WARNING)
    *   T-003: Network Failure/Time Out (ERROR - IO-TIMEOUT)
    *   T-004: Invalid Schema Input (ERROR - SCHEMA-BREACH)