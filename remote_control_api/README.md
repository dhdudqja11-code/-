# 🛠️ Remote Control API Gateway (MVP v1.0)

## ✨ 개요
본 서비스는 원격 제어 프로그램의 핵심 백엔드 로직을 담당하며, 최소한의 기능 단위(MVP)로 구현되었습니다. 모든 요청은 **OAuth 2.0** 기반의 인증과 **RBAC (Role-Based Access Control)** 검증을 거치도록 설계되었습니다.

## 📁 구조
- `schemas.py`: Pydantic 모델 및 데이터 스키마 정의.
- `security_utils.py`: 사용자 자격 증명 확인, 토큰 발행(더미), 권한 검사(Dummy) 로직 포함.
- `main.py`: FastAPI 엔드포인트 및 핵심 비즈니스 로직을 담는 메인 파일.

## 🔐 보안 아키텍처 (핵심 원칙)
1. **OAuth 2.0:** 모든 API 호출은 유효한 Bearer Token을 요구합니다. (`/auth/token` 사용)
2. **RBAC:** `get_current_user_with_rbac` 의존성을 통해 요청자가 최소한의 권한 레벨(OPERATOR, ADMIN 등)을 가졌는지 검사합니다.
3. **감사 추적 (Audit Trail):** 모든 중요한 액션(세션 시작, 명령어 실행)은 `audit_log_entry` 형태로 로그에 기록됩니다.
4. **데이터 파기 프로토콜:** 민감한 세션 데이터나 트랜잭션 정보는 API 응답으로만 전달되며, 실제 영구 저장소에는 암호화되어 분리된 별도의 로깅 시스템(ELK/Splunk)으로 전송되어야 하며, 일정 시간이 지나면 자동 파기(Purge)되는 절차가 필수입니다.

## 🧪 테스트 및 검증 (Testing & Validation)
### 1. Unit Test Structure (`test_api.py`)
각 모듈(`security_utils`, `schemas`) 별로 단위 테스트를 작성합니다. 특히, 권한 위반 시나리오(403 Forbidden)와 인증 실패 시나리오(401 Unauthorized)에 대한 테스트 케이스가 필수입니다.

### 2. Integration Test Structure (`test_e2e.py`)
실제 엔드포인트(`main.py`)를 호출하여 E2E 흐름을 검증합니다:
- **성공 경로:** `Login` $\to$ `Start Session` $\to$ `Execute Command (Admin)`
- **실패 경로 1 (권한):** `Login` $\to$ `Start Session` 시도 (Viewer 역할로 테스트) $\to$ 403 에러 확인.
- **실패 경로 2 (유효성):** 잘못된 요청 바디를 전송하여 Pydantic 유효성 검사 실패 확인.

## ⚙️ CI/CD 파이프라인 설계
| 단계 | 도구 | 목표 | 실행 조건 및 체크리스트 |
| :--- | :--- | :--- | :--- |
| **1. Linting** | `flake8`, `mypy` | 코드 스타일 및 타입 안정성 검사 | 모든 파일에서 린팅 통과 (Pass) 필수. |
| **2. Unit Test** | `pytest` | 개별 함수 및 모듈 로직 테스트 | 커버리지(Coverage) 최소 90% 목표. 특히 `security_utils`의 권한 체크 로직은 Mocking을 통해 철저히 검증해야 함. |
| **3. Integration Test**| `pytest` | API 엔드포인트 간의 흐름 및 계약 테스트 | 모든 End-to-End 시나리오(성공/실패)에 대해 200 OK 또는 적절한 에러 코드(401, 403 등)를 반환하는지 검증. |
| **4. Security Scan**| `bandit` (SAST) | 잠재적인 보안 취약점 분석 | 민감 정보 하드코딩, SQL Injection 패턴 등을 자동 감지합니다. 반드시 스캔 결과를 통해 수정해야 합니다. |
| **5. Deployment** | Docker/Kubernetes | 배포 환경 준비 및 오케스트레이션 | `Dockerfile`을 작성하여 가상 환경 의존성을 고정하고, API Gateway를 통해 로드 밸런싱 구성. |