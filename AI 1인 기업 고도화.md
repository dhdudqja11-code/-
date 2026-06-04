# 🏛️ AI 1인 기업 고도화 마스터 명세서

본 문서는 AI 1인 기업 시스템의 시각적 및 기능적 고도화 작업을 집대성한 최종 기술 명세서입니다. 오영범 작가님의 따뜻한 문체 브랜딩(세리프 타이포그래피, 웜 앰버 네온 광원)과 영화 아이언맨의 첨단 HUD 콘솔(Jarvis) 스타일의 비주얼 퀄리티를 결합하여 사용자 경험을 극대화하였습니다.

---

## 📅 작성 및 검증 정보
- **최종 검증 완료**: 2026-06-04
- **주요 적용 대상**: 
  1. Next.js 어드민 대시보드 ([admin/page.tsx](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/global-letters/src/app/admin/page.tsx))
  2. ConnectAI VS Code 익스텐션 가상 사무실 웹뷰 ([extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts))
- **컴파일/빌드 검증**: Next.js 프로덕션 빌드 및 esbuild 익스텐션 컴파일 완료 (Perfect Pass)

---

## 🗺️ 1. Next.js 어드민 대시보드 HUD 개편

기존의 단순한 관리자 화면을 대칭형 **3단 울트라 HUD 그리드** 형태로 개편하고, 웜 앰버 테마와 다크 글래스모피즘 스타일을 완벽히 주입했습니다.

### 1.1 주요 구성 요소 및 기술
* **중앙 공감 반응로 (Central Empathy Reactor)**:
  - 회전 및 맥박(pulsing) 치는 웜 앰버 색상의 기하학 하트 SVG 코어 애니메이션을 배치하여 시스템이 살아있는 듯한 연출을 부여했습니다.
  - 공감 온도(`98.6°F / 37.0°C`) 및 AI 가동 부하율, Windows 커널 스케줄러 상태(`BELOW_NORMAL_PRIORITY_CLASS (0x00004000) Active`) 정보를 모노스페이스 디지털 수치로 시각화했습니다.
* **10대 에이전트 진단판 HUD (Agent Diagnostics HUD)**:
  - 10대 에이전트(영숙, 코다리, 오영범 작가 등)의 현재 가동 상태를 실시간 LED 라이트(그린 펄스, 블루 대기, 레드 락다운)로 진단 표시하는 고화질 그리드를 탑재했습니다.
* **실시간 에이전트 소통 터미널 (Live Empathy Stream Terminal)**:
  - 흑색 반투명 바탕에 골드 네온 글씨가 깜빡이는 CLI 터미널 창을 디자인하여, 에이전트들이 유기적으로 상호작용하는 모의 로그를 타이프라이터 연출로 송출하도록 구현했습니다.
* **마스터 뇌 지식 주입기 (Knowledge Base Injector)**:
  - 텍스트 주입 장치 테마로 리모델링하여 지침 입력창은 `'JetBrains Mono'`로, 에세이 및 감성 글귀 입력창은 세리프체로 나누어 시각적 조화를 이루었습니다.
* **몬테카를로 리스크 레이더 (Monte Carlo Risk Radar)**:
  - PII 유출, 감사 로그 무결성 등 5대 리스크 지표 슬라이더를 장착하여, 조작 시 백엔드 ROI 공식에 연동된 **회피 가능한 잠재적 재무 손실액($A_{LP}$)**을 게이지 차트로 실시간 연산하여 시각화했습니다. 임계치 초과 시 붉은 경고등이 점멸합니다.

---

## 🏢 2. VS Code 익스텐션 가상 사무실 웜 앰버 HUD 리모델링

VS Code 내 가상 사무실의 비주얼과 레이아웃을 다크 글래스모피즘 테마의 웜 앰버 네온 HUD 테마로 전면 교체하여 일관된 브랜드 정체성을 유지했습니다.

### 2.1 CSS 변수 개편 (`:root`)
기존의 형광 녹색 매트릭스 테마에서 **따뜻하고 빛나는 웜 앰버/골드** 변수군으로 변경했습니다:
```css
:root {
  --accent: #F59E0B;          /* Warm Amber */
  --accent2: #D97706;         /* Darker Amber */
  --accent-glow: rgba(245, 158, 11, 0.22);
  --bg: #0C0A09;              /* Warm Obsidian */
  --bg2: #1C1917;             /* Stone Dark */
  --surface: rgba(28, 25, 23, 0.78);
  --border: rgba(245, 158, 11, 0.15);
  --text: #F5F5F4;            /* Soft White */
  --text-dim: #A8A29E;        /* Muted Warm Grey */
  --text-bright: #FFFFFF;
}
```

### 2.2 하이테크 HUD 비주얼 요소 고도화
* **24시간 자동화 스위치 (`#workdayBtn`)**:
  - 가동 시 회전(spin) 및 맥박(pulse) 형태의 웜 앰버 테두리 오라(Aura) 효과를 구현하여 아이언맨 아크 리액터의 시각적 피드백을 전달합니다.
  ```css
  @keyframes workdayLiveDot {
    0%, 100% { transform: scale(1); opacity: 1; filter: brightness(1); }
    50% { transform: scale(1.6); opacity: .5; filter: brightness(1.5); }
  }
  ```
* **탑바 (`.topbar`) & 브랜드 마크 (`.brand-mark`)**:
  - `backdrop-filter: blur(16px)`와 골드 앰버 그라데이션 및 섀도우를 입혀 공중 부유(Floating) HUD 느낌을 강조했습니다.
* **에이전트 펄싱 링 & 입자 이펙트**:
  - 작업 중인 에이전트 주변 골드/앰버 링의 파동 애니메이션을 고도화했습니다.
  - 가상 사무실에 동적으로 흩날리는 부유 먼지 입자(`spawnParticles`)들을 녹색/보라색 계열에서 앰버/골드/오렌지 빛 스파크(`rgba(245,158,11,.45)`) 톤으로 리터칭했습니다.

### 2.3 작가용 Serif 서체 주입 (브랜드 융합)
* 텍스트 주도의 주요 영역에 우아하고 편안한 세리프 서체(`Georgia, 'Times New Roman', serif`)를 적용해 감성적 무드를 융합시켰습니다:
  - **화이트보드 (`.whiteboard`)**: 가로형 브리핑 창에 세리프 폰트를 적용해 정보 가독성을 높였습니다.
  - **말풍선 (`.bubble`)**: 에이전트가 단독 발화 시 폰트 크기 `11px`과 이탤릭 장식이 적용된 따뜻한 세리프체를 표현합니다.
  - **활동 로그 (`.log-text`) 및 산출물 (`.out-body`)**: 세리프 서체를 적용해 문학적 성과의 깊이를 강조했습니다.

---

## 🔍 3. 종합 검증 및 빌드 확인

### 3.1 Next.js 어드민 대시보드
* **결과**: `npm run build` 결과, 코드 상의 타입 충돌이나 레이아웃 경고 없이 깨끗하게 프로덕션 빌드가 성공했습니다.

### 3.2 ConnectAI VS Code Extension
* **결과**: `ConnectAI` 폴더 내 `npm run compile` 실행 시 `esbuild` 번들러를 통해 `out/extension.js` (1.4MB) 파일이 205ms만에 오류 없이 완전하게 빌드 완료되었습니다.
  ```powershell
  npm run compile
  ```
