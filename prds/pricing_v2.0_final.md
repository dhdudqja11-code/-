# 🚀 PRD: '마음을 묻다' 구독 플랜 v2.0 (Monetization & API Gateway Level)
**버전:** 2.0
**작성자:** 현빈 (Head of Business Strategy)
**목표:** 고객의 잠재적 위험 인지(Pain Point)를 극대화하여, 가장 높은 가치와 통제력을 제공하는 Enterprise 플랜으로의 전환율을 최적화하고, 핵심 분석 기능에 대한 유료 게이팅 로직을 명확히 정의한다.

## 1. 비즈니스 목표 및 KPI (Business Objectives & KPIs)
**최종 Goal:** 고객이 스스로 "현재 상태로는 충분하지 않다"고 느끼게 만들어, 최소한 Pro 플랜 이상의 구독을 하도록 유도하는 것.
**핵심 지표 (KPIs):**
*   Conversion Rate (CR): Free Trial $\rightarrow$ Paid Subscription 전환율 증가 (목표: 15% 이상).
*   Average Revenue Per User (ARPU): 사용자당 평균 매출 증대 (Enterprise 플랜 비중 확대 유도).
*   Feature Usage Gap: Basic/Pro 간의 핵심 기능 사용 빈도를 분석하여, Pro로의 업그레이드 필요성을 느끼게 만드는 지점(Gap)을 자동 감지하고 노출해야 함.

## 2. 구독 레벨별 가치 제안 및 제한 사항 (Value Proposition & Limitations)
| 구분 | Basic Plan (Free/Trial) | Professional Plan (Paid) | Enterprise Elite (Premium) |
| :--- | :--- | :--- | :--- |
| **가치 포지셔닝** | *진단*의 시작점. 간단한 위험 인지 및 자기 점검 도구. | *분석*과 *개선*. 복합적 요인 분석 및 구체적인 대응책 제시. | *통제*와 *자동화*. 시스템 레벨의 리스크 관리 및 의사결정 지원. |
| **핵심 기능 (Included)** | 1회성 '기본 위험 지수' 산출. 주요 규제 위반 항목 알림 (Static). | **[유료 게이팅]** 다중 변수 기반 'Avoided Loss' 정밀 분석 실행 (최대 5개 요인 조합). 맞춤형 리스크 보고서 다운로드 (PDF/PPT). | **[API Gateway Required]** API 엔드포인트 직접 호출 및 데이터 주권 모니터링 자동화. 전담 컨설턴트 연동 및 실시간 규제 변화 피드 제공. |
| **분석 범위 제한** | 단일 산업군, 정적(Static) 위험 요소만 검토 가능. | 다중 산업군 비교 분석, 동적(Dynamic) 시나리오 기반 예측 모델 사용. | 무제한 데이터 볼륨 처리, 고객사의 내부 시스템과의 E2E 통합 연동 지원. |
| **가장 큰 Pain Point** | "이게 정말 나에게 맞는 리스크인가?" (추상적 불안감만 해소). | "**어떻게 고쳐야 하는지?**"에 대한 구체적인 로드맵과 실행 가능성을 제시함. | "**이미 벌어진 후의 사후 대응**"까지 아우르는 완벽한 시스템 통제권을 제공함. |
| **가격 근거 (Monetization Anchor)** | 0원 (데이터 수집 목적) | **[가치]:** 시간당 컨설팅 비용 절감액으로 책정. / **[근거]:** 고성능 컴퓨팅(HPC) 자원 사용료, 데이터 처리 복잡성에 비례. | **[가치]:** 잠재적 법률/규제 리스크 회피 비용 (사고 발생 시 최소 억 단위). / **[근거]:** 시스템 통합(Integration), 전담 인력 및 지속적인 업데이트에 대한 SLA 제공. |

## 3. 개발자 요구사항 명세 (PRD - Technical Specification)
개발팀은 다음의 논리적 흐름을 API Gateway 레벨에서 구현해야 합니다. 이는 단순한 플래그 체크가 아니라, **호출 시점의 권한 검증(Authorization)** 단계에 녹아들어야 합니다.

**A. Core Logic Flow (API Gateway Middleware):**
1.  `Client_Request` $\rightarrow$ `Gateway_Auth()`: 구독 레벨 확인 (Basic/Pro/Enterprise).
2.  `Gateway_Validation()`: 요청된 분석 기능의 복잡도(Complexity Score) 및 데이터 볼륨을 계산.
3.  **[Monetization Gate Check]**: 요청된 기능이 현재 플랜에서 제공하는 최대치를 초과할 경우, **HTTP 403 Forbidden** 응답을 반환하며, 사용자에게 "더 깊은 통찰력(Insight)"을 위해 상위 플랜으로 업그레이드하도록 유도하는 구체적인 가이드 메시지를 포함해야 함.

**B. 핵심 기능별 게이팅 로직 (Gating Logic):**
*   Basic $\rightarrow$ Pro: '단일 위험 지수' 요청은 허용하나, `Avoided Loss` 계산 실행을 시도할 경우 플랜 제한 초과 에러 발생.
*   Pro $\rightarrow$ Enterprise: 보고서 다운로드 기능에 대한 횟수(Quota)를 설정해야 함. Pro는 월 N회까지 무료 제공하고, 추가 사용 시 Enterprise의 '무제한 API 접근'을 강제하도록 설계한다.

## 4. 디자인/UX 요구사항 (Design & UX Notes)
*   **Pricing Page:** Basic $\rightarrow$ Pro $\rightarrow$ Enterprise로 이어지는 흐름에서, Pro 플랜이 **가장 눈에 띄는 위치(Golden Spot)**에 배치되어야 합니다. 이는 '대부분의 사용자가 가장 먼저 필요성을 느끼는 지점'을 공략하기 위함입니다.
*   **Report Download:** Basic 플랜에서는 결과만 제공하고, PPT/PDF 등 구조화된 리포트 다운로드는 Pro 이상에서만 가능하게 하여 물리적 가치(Tangible Value)를 높여야 합니다.