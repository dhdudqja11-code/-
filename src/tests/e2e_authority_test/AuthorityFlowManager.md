# 🛡️ 시스템적 권위(Systemic Authority) E2E 통합 테스트 아키텍처 보고서 v1.0
## 🎯 목표 및 핵심 원칙
본 모듈의 목적은 단순히 '기능이 작동하는가'를 검증하는 것이 아니라, **시스템이 오류 상황에서도 통제권을 유지하고 구조화된 해결책을 제시할 수 있는지**를 기술적으로 증명하는 것입니다. 모든 테스트 케이스는 다음 3단계 플로우를 강제합니다:
1.  **Initial State (초기):** 정상 작동 또는 초기 진단 시작.
2.  **Warning State (경고):** 리스크 발생(Compliance Breach) $\rightarrow$ $L_{reg}$ 계산 및 경고 메시지 출력.
3.  **Resolution State (해결):** 시스템이 스스로 통제권을 확보하고 해결책을 제시하며 최종 상태로 전이.

## 🏗️ 아키텍처 컴포넌트 구조
![Architecture Diagram Placeholder: Initial -> Warning (Breach) -> Resolution Flow](https://i.imgur.com/example_authority_flow.png) 
*(실제 구현 시, 이 다이어그램은 StateManager 클래스 및 관련 모듈을 참조해야 합니다.)*

### 📂 모듈 분리 계획
| 모듈 | 역할 (Responsibility) | 핵심 책임 | 의존성 |
| :--- | :--- | :--- | :--- |
| `AuthorityClient` | 외부 데이터/API 호출 시뮬레이터. | API 응답 구조화, 강제적인 Failure/Timeout 주입. | None |
| `StateManager` | 시스템 상태 전이 로직의 심장부. | 현재 상태를 추적하고, 다음 상태로 이동할 때 필요한 액션(경고 메시지 생성 등)을 정의. (State Pattern 적용) | `AuthorityClient`, `SchemaDefinitions` |
| `TestSuiteRunner` | 테스트 케이스 실행기. | 각 시나리오에 따라 `StateManager` 호출 $\rightarrow$ 결과 검증 및 보고서 기록. | `StateManager` |

## 🧪 데이터 흐름 (Mock API Interaction)
1.  **Input:** 트랜잭션 정보 + KPI 측정값 (e.g., Proof of Erasure Score).
2.  **Client -> StateManager:** `AuthorityClient.get_authority(data)` 호출.
3.  **StateManager:** 결과가 임계치 미만인 경우 $\rightarrow$ **Warning State** 진입.
4.  **State Transition Logic:** Warning 메시지 구조화 (What/Why/How) 및 $L_{reg}$ 계산.
5.  **Output:** 구조화된 최종 보고서 (JSON Schema 준수).

### 🔑 핵심 데이터 스키마 정의
모든 모듈은 다음의 **AuthorityCheckResponseSchema**를 따릅니다. 이는 시스템적 권위를 기술적으로 강제하는 최소한의 약속입니다.
*   `status`: ("SUCCESS", "WARNING", "ERROR") - 현재 상태.
*   `authority_score`: (Float) - 통제권 점수.
*   `diagnosis`: {What went wrong?} - 문제 정의.
*   `root_cause`: {Why did it go wrong?} - 원인 분석 및 KPI 위반 지점 명시.
*   `mitigation_steps`: {How to fix it?} - 구체적인 해결책 (Actionable Items).