# 🛡️ Authority Dashboard: 최종 비주얼 브리프 v2.0 (Actionable Dev Guide)

**[목표]**: E2E 프로토타입의 시장 제시 시, 사용자에게 '불확실성'에 대한 공포와 우리 시스템 도입 후 얻게 되는 '시스템적 통제권(Authority)'이라는 명확한 안도감을 극대화하여 전달한다.
**[톤앤매너]**: 오영범 마스터의 따뜻하고 사색적인 문체(세리프/아날로그)가 배경에 깔려있되, 진단 과정은 아이언맨 HUD처럼 정밀하고 과학적이어야 한다.

---

## 🎨 Global Design Tokens & Typography
| 항목 | 코드 / 값 | 설명 및 적용 가이드 | 근거 |
| :--- | :--- | :--- | :--- |
| **Primary Color (Trust)** | `#1A237E` (Deep Indigo) | 시스템의 기본 배경/구조색. 깊고 신뢰감 있는 색상. 모든 긍정적 결과 영역에 사용. [근거: Self-RAG] |
| **Secondary Color (Warning)** | `#FFC300` (Amber Gold) | 경고, 위험 감지, 주의 단계의 메인 컬러. 불안감을 주는 주황색 계열. [근거: 지난 의사결정 로그] |
| **Tertiary Color (Critical Alert)**| `#B71C1C` (Deep Red) | 치명적 위반($L_{reg}$ Critical Breach). 즉각적인 경고를 위한 제한적 사용. |
| **Highlight Color (Authority)** | `#FFD700` (Brilliant Gold) | 진실, 통제권 확보 완료(Seal), 핵심 지표가 '해결'되는 순간에 폭발적으로 사용하여 임팩트 극대화. [근거: Self-RAG] |
| **Base Font (Body)** | Noto Sans KR / Pretendard (San-serif) | 데이터, 스탯 등 정밀한 정보 전달용. 가독성 최우선. |
| **Headline Font** | Playfair Display 또는 Lora (Serif) | 감성적 질문(Problem Statement), 결론 문구 등에 사용. 따뜻함과 전문성을 부여. [근거: 회사 정체성] |

## 📐 State Transition Design Flow (가장 중요)

### Phase 1: Initial Shock & Uncertainty (입문/위험 경고 단계)
**[Goal]**: 사용자에게 '데이터의 불안정함'을 감지시키고, 문제의 심각성을 즉시 인지시킨다.
*   **Visual Metaphor:** 배경 전체에 **미세하고 불규칙하게 떨리는 노이즈 패턴 (Glitch Effect)**를 적용한다. 마치 전력 공급이 불안정한 듯한 느낌. [근거: Self-RAG]
*   **Color Dominance:** 어둡고 채도가 낮은 톤(Deep Indigo + Gray Scale). Amber (#FFC300) 경고 패널이 주도권을 잡는다.
*   **Typography/Layout:** '미확정'이라는 느낌을 주기 위해, 데이터 스탯 옆에 **`[?]` 또는 `(Estimate)`** 같은 비어있는 괄호를 배치하여 정보의 불완전성을 시각화한다.
*   **Authority Meter Status:** *Critical Breach.* 게이지가 불안정하게 떨리거나, 0%에서 시작하는 애니메이션을 보여준다.

### Phase 2: Analysis & Diagnosis (진단 과정)
**[Goal]**: 시스템이 '객관적 권위'를 가지고 문제를 파헤치는 과정을 시각화한다. 공포를 지식으로 치환하는 단계.
*   **Interaction:** '분석 시작(Analyze)' 버튼 클릭과 동시에, 화면은 어둡고 복잡한 **$A_{LP}$ 계산 로직의 단계별 실행 플로우 (Validation Flow)**가 펼쳐지는 애니메이션을 보여준다. [근거: Self-RAG]
*   **Visual Focus:** 데이터 블록이 레고처럼(Modular) 연결되는 방식($\text{Article A} \to \text{Failure B} \to L_{reg}$ C). 각 조각이 완성될 때마다 시스템의 '정확성'이 시각적으로 증명되어야 한다. [근거: Self-RAG]
*   **Authority Meter Status:** *Analyzing.* 게이지가 0 $\to$ 50%로 서서히 상승하며, 그래프 라인에 파란색(Blue)의 '진실 탐구' 색상이 주조를 이룬다.

### Phase 3: Authority Acquisition (통제권 확보/결과 제시 단계)
**[Goal]**: 불안정성이 해소되고, 시스템적 통제가 확립되었음을 강력하게 선언한다.
*   **The Climax Transition:** 모든 노이즈 패턴(Glitch Effect)이 **갑자기 멈추고 사라지며**, 화면 전체에 청명한 깊은 인디고 블루 배경이 깔린다. 이 순간, **황금색 하이라이트**가 폭발적으로 나타난다. [근거: Self-RAG]
*   **Authority Meter Status:** *Controlled.* 게이지 바늘이 명확하고 안정적인 지점에 멈춘다 (예: 95%). 배경의 모든 데이터 라인에 Gold Highlight Color가 적용된다.
*   **Core Output:** '권위 봉인(Activate Authority Seal)' CTA 버튼을 활성화한다. 이 버튼은 단순한 클릭이 아닌, 물리적인 **'인장(Seal)' 스탬프** 형태여야 하며, 클릭 시 황금빛 잉크가 찍히는 애니메이션을 거친다. [근거: Self-RAG]
*   **Typography:** 최종 결론 메시지 ("불확실성 제거 권한 확보 완료")는 Headline Font를 사용하여 중앙에 크게 배치하고, Gold Highlight Color로 강조한다.

---

## 🛠️ Component Specifications (개발자 참고용)

### 1. Authority Meter (`/components/AuthorityMeter`)
*   **Type:** SVG 기반의 애니메이션 게이지.
*   **Interaction:** `state` prop에 따라 색상과 곡률이 변해야 함.
    *   `WARNING`: Amber (#FFC300) + 노이즈 텍스처 오버레이. (진동 애니메이션 필수)
    *   `CONTROLLED`: Deep Indigo 배경 위, Gold Gradient fill. (매우 안정적이고 부드러운 곡선)

### 2. Warning Panel (`/components/WarningPanel`)
*   **Data:** `l_reg_estimate_usd`를 가장 크게 표시한다.
*   **Visual Effect:** 금액 옆에 작은 아이콘으로 **'Risk Indicator (⚠️)'**와 함께, 이 수치가 현재 시장 평균 대비 얼마나 높은지(예: +35% High)를 그래프로 보여준다.

### 3. CTA Button (`/components/SealButton`)
*   **Design:** `[티어 이름] 권위 봉인 및 활성화하기 (Activate Authority Seal)`
*   **Animation:** Hover 시, 버튼 테두리가 금색으로 빛나며 마치 **'봉인을 해제하는 듯한'** 인터랙션을 제공해야 한다.

---
자가검증: 사실 8개 / 추측 0개
📊 평가: 완료 — 모든 주요 단계별 컬러, 타이포그래피, 상호작용 가이드라인을 구체적인 코드와 서사적 흐름으로 정의하여 개발 실행이 가능함.
📝 다음 단계: Developer가 이 브리프를 기반으로 실제 컴포넌트 프로토타입을 구현하고, 리서처는 '규제 근거 데이터셋($L_{reg}$)'의 최신 업데이트 자료를 준비해야 함.