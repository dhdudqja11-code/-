# Mini ROI Simulation: Critical State Handoff Specification v1.0

## 🎯 핵심 목표 및 원칙
*   **목표:** 사용자의 '위기감 $\rightarrow$ 긴급성 $\rightarrow$ 해결책 제시'의 감정적 여정을 극대화하여 유료 전환을 유도한다.
*   **원칙:** 법적 근거(Statute Citation)와 정량화된 재무 손실액($M)을 중심으로 권위적인 톤앤매너를 유지하며, 모든 위기 상태는 애니메이션과 대비되는 순간 명료한 해결책으로 전환되어야 한다.

## 🎨 비주얼 디자인 시스템 스펙
| 요소 | 상세 규격/코드 | 역할 및 지침 |
| :--- | :--- | :--- |
| **Primary (Assurance)** | `#007AFF` | 신뢰, 해결책 제시. CTA 버튼 기본 색상. |
| **Warning (Critical)** | `#D9263C` | 즉각적 위험 경고. 깜빡임(Flash Rate: 1~2Hz) 애니메이션 필수. |
| **Base Color** | `#F0F0F5` | 표준 배경색. 위기 시 어두운 회색(`#33334D`)으로 전환되는 대비가 핵심. |
| **Typography** | Pretendard / Noto Sans KR (Bold/Black) | 수치와 법적 근거는 다른 텍스트보다 최소 20% 크게, 그리고 과감하게 배치한다. |

## ⚙️ 인터랙션 플로우 및 상태별 로직 (Handoff Blueprint)
### State 1: 초기 진단 (Neutral) $\rightarrow$ State 2: 리스크 감지 (Critical)
*   **Trigger:** 데이터 제출 또는 시간 기반 자동 실행.
*   **Animation:** 배경색이 `#F0F0F5` $\rightarrow$ 어두운 회색(`#33334D`)으로 **0.5초 Fade Out/In**. 화면에 미세한 노이즈 필터(Static Noise Overlay)가 적용된다.
*   **Alert:** 중앙 상단에 `[🚨 CRITICAL COMPLIANCE VIOLATION DETECTED]` 배너가 `#D9263C`로 깜빡이며 고정됩니다.

### State 2: 리스크 감지 (Critical) $\rightarrow$ State 3: 손실액 정량화 (Panic)
*   **Focus:** 불안정한 데이터 시각화(Graph Jitter).
*   **Animation:** ROI 그래프가 빨간색으로 변하며, 데이터 포인트들이 무작위로 크게 진동하는 애니메이션을 보여준다.
*   **핵심 로직:** 중앙에 'Estimated Loss Exposure' 수치를 배치하고, **0초부터 목표 금액($X.XM)까지 3초 동안 카운트업(Animated Counter Up)**되도록 구현한다.

### State 3: 손실액 정량화 (Panic) $\rightarrow$ State 4: 해결책 제시 (Assurance)
*   **Trigger:** 시스템 개입 로직 실행.
*   **Animation:** 화면 전체가 **`Assurance Blue` 계열의 빛(Flash/Wipe Effect)**으로 순간적으로 덮이면서 시각적 충격을 전환한다 (Transition Time: 0.2s).
*   **Display Change:** 혼란스러운 빨간색 그래프는 사라지고, '위험 원인 $\rightarrow$ 시스템 개입 $\rightarrow$ 결과'의 **3단계 플로우차트(Flowchart)**가 깨끗한 Grid 레이아웃으로 재배치된다.
*   **CTA 활성화:** 하단에 `Assurance Blue` 배경의 CTA 버튼이 등장하며, 마우스 오버 시 미세하게 Glow Effect를 적용한다.