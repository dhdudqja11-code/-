# Mini ROI 시뮬레이터 E2E 테스트 구조 정의서 (v1.0)

## 🎯 목적
본 문서는 Mini ROI Simulator의 전체 라이프사이클(사용자 입력 $\rightarrow$ 로직 처리 $\rightarrow$ 외부 API 호출 $\rightarrow$ 결과 출력)에 걸친 모든 기능적/비기능적 안정성을 검증하기 위한 End-to-End 테스트 스위트의 구조와 기준을 정의한다. 단순 성공 케이스(Happy Path)를 넘어, 실제 운영 환경에서 발생 가능한 네 가지 핵심 실패 상태(Failure State)에 대한 방어 로직이 필수적으로 포함되어야 한다.

## 🧪 사용 프레임워크 및 도구
*   **프레임워크:** Pytest (Python Testing Framework)
*   **모킹:** `unittest.mock` 또는 `pytest-mock` (외부 API 호출, DB 접근 등 사이드 이펙트 격리 목적)
*   **스트레스 테스트:** Locust 또는 직접 구현한 반복 루틴

## 🗺️ 테스트 스위트의 구조 (Test Coverage Matrix)

| # | Failure State | 검증 목표 | 필수 Mocking/테스트 기법 | 기대하는 핵심 방어 로직 |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **외부 API 연동 실패** | 외부 리스크 데이터 (예: 규제 DB) 호출 시 다운, Timeout 발생 상황 처리. | `requests` 라이브러리 Mocking (`MockResponse`) | **Circuit Breaker 패턴 적용.** 3회 이상 연속 실패 시 시스템 차단 및 대체 로직(Fallback Data) 활성화. 사용자에게는 "현재 데이터 연동에 어려움이 있습니다. 잠시 후 다시 진단해주세요."와 같은 명확한 안내 제공. |
| **2** | **사용자 입력 오류 (Bad Input)** | 숫자만 기대하는 필드에 문자열, `null`, 비어있는 값 등 잘못된 유형의 데이터가 들어왔을 때 처리. | Pytest Fixture를 이용한 Bad Data Payload 주입. Pydantic Validation Mocking. | **Pydantic/Type Hint 검증 강제.** 입력 단계에서 에러 발생 시, 구체적인 필드별 오류 메시지(e.g., "재무 손실액은 숫자여야 합니다.")와 함께 입력을 즉시 중단시키고 사용자에게 피드백. |
| **3** | **권한 초과/데이터 누락** | 사용자가 접근할 수 없는 데이터에 요청하거나, 필수 입력 변수(Source, Time 등)가 빠졌을 때. | Mocking API Gateway를 통해 권한 체크 로직 가로채기. 테스트 케이스에서 `None` 값 명시적 주입. | **ACL/RBAC 검증 의무화.** 백엔드 레이어에서 접근 시도 전 모든 데이터에 대한 소유권 및 접근 레벨을 1차 필터링하고, 실패 시 '403 Forbidden' 응답과 함께 권한 부족 사유를 명시적으로 반환. |
| **4** | **시스템 과부하 (Stress Test)** | 짧은 시간 내 대량의 요청(High Concurrency)이 들어왔을 때 시스템 성능 및 안정성 검증. | Locust/Asyncio 기반 동시 요청 시뮬레이션. 부하 분산 테스트. | **Rate Limiting & Queueing.** Redis 등의 캐싱 레이어와 Rate Limiter를 통해 트래픽을 조절하고, 초과 요청은 '현재 서비스가 혼잡합니다. 잠시 후 다시 진단해주세요.' 메시지와 함께 큐(Queue)에 대기시켜 재진입성을 확보. |

## 🛠️ 구현 가이드라인
*   **테스트 커버리지:** 모든 비즈니스 로직 함수는 최소한 한 개의 실패 케이스 테스트를 가져야 한다.
*   **결과 기록:** 각 테스트 실행 시, 성공/실패 여부와 함께 **시스템이 반환한 에러 코드 및 사용자에게 노출된 메시지**를 상세히 로그로 남겨야 한다.