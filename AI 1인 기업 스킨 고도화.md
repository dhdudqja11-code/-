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

---

## 🌿 3. '마음을 묻다' 감성 가상 사무실 개편 및 에이전트 재배치

'마음을 묻다' 프로젝트의 '밤의 정원' 웰니스 치유 컨셉에 부합하도록 가상 사무실의 배경과 에이전트 배치를 전면 개편했습니다.

### 3.1 배경 맵 로드 버그 수정 및 에러 가드
*   **배경 파일**: `ConnectAI/assets/map.jpeg`
*   **조치**: 
    1. `extension.ts`의 `_resolveCustomOfficeMap()` 내의 경로 정규화 및 탐색 경로(extAssets) 검증 로직을 고도화하고, 예외 발생 시 에러 로그를 상세히 출력하도록 `try-catch` 디버깅 로깅을 보강했습니다.
    2. **[최종 추가 조치]**: 로컬 워크스페이스 경로(`c:\Users\user\AI 기업 두뇌\내 작업들`)에 한글과 공백이 포함되어 있어 CSS `url()` 호출 시 파싱 에러로 렌더링이 실패하던 고질적 웹뷰 버그를 수정했습니다. 리소스 URI(`customMapUri`, `grassUri`, `pathUri`, `sprite`)를 CSS `url()` 내에서 홑따옴표 `'`로 감싸 파싱을 정상화시켰으며, `npm run compile` 빌드를 거쳐 복구를 완료했습니다. (반영을 위해 `Developer: Reload Window` 필요)

### 3.2 '밤의 정원' 감성 쉼터 구역 (Zones) 개편
커스텀 맵 로딩 시 기존 '회의실/복사실' 대신 감성 쉼터 구역 3가지로 오버라이드되도록 설계하였습니다.
*   **밤의 정원 벤치 (🌳)**: `x: 85, y: 32` (우측 하단 서재 구역 부근)
*   **공감 명상실 (🧘)**: `x: 50, y: 40` (중앙 라운드 테이블 부근)
*   **따뜻한 차 테라스 (🍵)**: `x: 70, y: 60` (카페/식음료 바 부근)

### 3.3 에이전트 10인 감성 명칭 및 직함 개편 (`agents.ts`)
기존의 차갑고 기술 중심적인 명칭을 '마음을 묻다'의 영혼에 맞게 감성적이고 정교한 역할명으로 전면 변경했습니다:
*   **오영범** (대표 & 마음치유 마스터, 🧭)
*   **영숙** (안내 & 고객 마음 돌봄 비서, 📱)
*   **레오** (유튜브 치유 콘텐츠 크리에이터, 📺)
*   **인스타** (소셜 감성 브랜딩 디렉터, 📷)
*   **디자이너** (감성 비주얼 아티스트, 🎨)
*   **코다리** (치유 시스템 엔지니어, 💻)
*   **현빈** (수익화 & 지속 가능성 파트너, 💼)
*   **루나** (BGM & 감성 사운드 디자이너, 🎵)
*   **작가** (위로와 공감의 에세이스트, ✍️)
*   **리서처** (치유 데이터 & 트렌드 탐색가, 🔍)

### 3.4 에이전트 가상 사무실 배치도 바닥 재배치 (2026-06-05 적용 완료)
에이전트들이 밤의 정원 맵에서 허공이나 벽에 어색하게 서 있지 않고, 중앙 및 우측의 나무 데크 바닥과 온실 내부 바닥 영역에 자연스럽게 자리 잡도록 배치 좌표를 수정했습니다.
*   **수정 파일**: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts) (`CUSTOM_MAP_DESKS` 객체)
*   **적용된 세부 좌표**:
    *   **오영범** (ceo): `{ x: 45, y: 42 }` (데크 중앙 위쪽)
    *   **영숙** (secretary): `{ x: 48, y: 48 }` (데크 중앙)
    *   **디자이너** (designer): `{ x: 55, y: 52 }` (데크 중앙 우측)
    *   **코다리** (developer): `{ x: 62, y: 56 }` (데크 중앙 우측)
    *   **현빈** (business): `{ x: 68, y: 60 }` (데크 우측)
    *   **루나** (editor): `{ x: 58, y: 68 }` (데크 아래쪽)
    *   **작가** (writer): `{ x: 66, y: 72 }` (데크 아래쪽)
    *   **리서처** (researcher): `{ x: 74, y: 76 }` (데크 아래쪽 우측)
    *   **레오** (youtube): `{ x: 78, y: 46 }` (온실 내부 바닥)
    *   **인스타** (instagram): `{ x: 82, y: 52 }` (온실 내부 바닥)

### 🧪 3.5 빌드 및 통합 테스트 최종 검증 결과
*   **ConnectAI 익스텐션 컴파일**: `npm run compile` 완료 (esbuild 62ms만에 무결성 빌드 완료)
*   **global-letters (Next.js 어드민)**: `npm run build` 프로덕션 빌드 완료 (Turbopack 빌드 성공 및 정적 최적화 완료)
*   **Python 백엔드 및 통합 테스트**: `python -m pytest` 실행 시 `api_gateway`, `processor`, `tests` 등 총 49개 핵심 모듈 통합 테스트 100% Perfect Green 통과 완료 (49 passed)

---

## 🛋️ 4. 가상 사무실 에이전트 대비 가구 크기 비율 최적화 (2026-06-05 적용 완료)

가상 사무실 내의 🪑, 🌳, 🛋️ 등 가구를 나타내는 이모지 마커의 크기가 픽셀 에이전트 캐릭터의 스케일에 비해 과도하게 컸던 불균형을 최적화하여, '밤의 정원' 컨셉의 전체 스킨 정체성을 유지하면서 조화로운 비주얼 밸런스를 이뤄냈습니다.

*   **수정 파일**: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts) (`.location`, `.location .loc-icon`, `.location .loc-label` 관련 CSS 규칙)
*   **세부 수정 내역**:
    *   **이모지 크기 (`.loc-icon`)**: `18px` ➡️ `12px`로 축소 조정하여 픽셀 에이전트 캐릭터와의 물리적 스케일 비율 조정.
    *   **레이블 텍스트 크기 (`.loc-label`)**: `7px` ➡️ `6px` / 자간 `1.5px` ➡️ `1px`로 정교화.
    *   **마커 박스 스타일**: 패딩 `4px 8px` ➡️ `2px 5px`, 보더 래디우스 `8px` ➡️ `5px`로 콤팩트하게 다듬어 맵 배경을 방해하지 않고 세련되게 스며들도록 수정.
    *   **배경 및 드롭 섀도우**: `rgba(8, 10, 15, .75)` 반투명 다크 필터와 은은한 하단 그림자(`box-shadow: 0 2px 6px rgba(0, 0, 0, .5)`) 연동.

---

## 🎨 5. 사이드바 에이전트 툴팁 및 3D Hover Tilt 고도화 (2026-06-05 적용 완료)

사이드바 대화창과 에이전트 상세 카드 영역의 상호작용성 및 시각적 몰입감을 영화 HUD 콘솔 급으로 끌어올렸습니다.

*   **수정 파일**: [sidebar.html](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/webview/sidebar.html), [agents.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/agents.ts)
*   **세부 고도화 내역**:
    *   **감정/이성 스탯 바인딩**: `agents.ts`에 각 에이전트별 페르소나를 반영한 감정 지수(Empathy), 이성 수치(Reasoning), 따뜻함(Warmth) 스탯 필드를 확장하고, 아바타 호버 시 나타나는 프리미엄 **Glassmorphism 미니 툴팁**에 게이지 바 형태로 렌더링했습니다.
    *   **메시지 카드 3D Hover Tilt**: 마우스 포인터의 실시간 상대 좌표를 추적하여 카드가 3D 공간 위에서 부드럽게 기우는 입체 반응을 구현하고, 감속 스프링백 복원 모션 및 동적 그림자를 연동했습니다.
    *   **무결성 검증 테스트**: `validate_virtual_office.js`, `validate_sidebar.js`, `validate_envelope.js` 세 개 스크립트를 통해 모든 고도화가 버그와 오작동 없이 안전하게 통과됨을 완벽하게 확인했습니다.

---

## 🌸 6. '밤의 정원' 배경 맵 재생성 및 대시보드 웜 앰버 통합 (2026-06-05 적용 완료)

질문 인터뷰(`/grill-me`)에 따라 감성 힐링 웰니스의 전체적인 일체감을 극대화하기 위해 스킨 디자인을 한 단계 더 끌어올렸습니다.

*   **배경 맵 재생성 (`map.png`)**:
    *   밤의 고요하고 따뜻한 정원 숲 분위기를 연출하기 위해, 풍부하고 화려한 금빛 등불조명, 야외 나무 데크, 온실 서재가 유기적으로 융합된 고품질 2D 픽셀 아트를 생성하여 [map.png](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/map.png) 경로에 적용 완료했습니다.
*   **대시보드 CSS 테마 통합 (`dashboard.css`)**:
    *   대시보드 변수군 `:root`의 살구/연보라색 톤을 가상 사무실 테마와 동기화하기 위해 **웜 앰버, 골드, 웜 옵시디언** 톤으로 완전히 갱신했습니다.
    *   `body::before` 내의 그라데이션 글로우를 웜 앰버 및 골드 글로우로 변경하여 화면 접속 시 아늑한 분위기를 뿜어내도록 리모델링했습니다.
*   **컴파일 및 빌드 확인**:
    *   `npm run compile` (익스텐션 컴파일) 및 `npm run build` (Next.js 어드민 빌드)가 오류 없이 완수되었음을 확인했습니다.

---

## 🌿 7. 가상 사무실 3D Hover Tilt 비활성화 및 ROI 시뮬레이터 이식 (2026-06-05 적용 완료)

밤의 정원 가상 사무실의 비주얼 사용성과 '마음을 묻다' 치유 비즈니스의 기능적 연결성을 한 단계 더 끌어올렸습니다.

*   **채팅 패널 3D Hover Tilt 비활성화**:
    *   **수정 파일**: [sidebar.html](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/webview/sidebar.html)
    *   **조치**: 마우스 포인터의 상대 위치에 따라 대화창 메시지 카드가 3D 공간 상에서 기울어지는 반응형 틸팅 마우스 이벤트를 비활성화 처리하여, 카드 가독성을 정적이고 평평하게 고정했습니다.
*   **글로벌 치유 비즈니스 ROI & 결제 퍼널 시뮬레이터 추가**:
    *   **수정 파일**: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts) (`_renderHtml`)
    *   **조치**:
        *   가상 사무실 화면 하단 영역에 5단계 결제 퍼널 및 매출 모의 연산을 위한 **Glassmorphism ROI Simulator 패널**을 이식했습니다.
        *   일일 유입 트래픽($100 \sim 10,000$명), 평균 치유 공감도($50\% \sim 100\%$), 프리미엄 결제 전환율($0.5\% \sim 15.0\%$)을 각각 세밀하게 조절하는 슬라이더 컨트롤을 탑재했습니다.
        *   슬라이더 조작 시, 5대 요금제 티어(`Random` 무료, `Free` 안부, `Beta` 5천원, `Deep` 9천원, `Recovery` 2.9만원)의 모의 유입량 분배율이 실시간 게이지 바로 가시화되며, 일일 예상 매출액 및 월간 예상 기대수익이 즉각 연동 연산되어 반영되는 반응형 JS 엔진을 연동했습니다.
*   **컴파일 및 E2E 시뮬레이션 무결성 검증**:
    *   `ConnectAI` 익스텐션 컴파일(`npm run compile`) 빌드가 타입 충돌 없이 성공적으로 완수되었습니다.
    *   `python simulator_v1/test_simulator.py` E2E 5대 시나리오 무결성 테스트가 Perfect Green으로 정상 통과되었습니다.

---

## 🏵️ 8. 매출 대시보드 스킨 고도화 및 백엔드 테스트 복구 (2026-06-12 적용 완료)

'밤의 정원 & 웜 앰버' 브랜드 아이덴티티와 연계된 매출 대시보드(Revenue Dashboard)의 시각적 리모델링을 마치고, 백엔드 테스트 스위트의 임포트 에러를 복구하여 통합 테스트 전량 패스를 달성했습니다.

*   **수정 파일**:
    - Webview 리모델링: [revenue-dashboard.css](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/webview/revenue-dashboard.css), [revenue-dashboard.js](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/webview/revenue-dashboard.js)
    - 익스텐션 구문 오류: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
    - 백엔드 상태 관리자: [authority_state_manager.py](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/src/services/authority_manager/authority_state_manager.py)
    - 라우터 직렬화: [authority_router.py](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/src/api_gateway/authority_router.py)
    - 테스트 시나리오 버그 수정: [test_suite.py](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/src/tests/e2e_authority_test/test_suite.py), [e2e_authority_test.py](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/tests/e2e_authority_test.py)
*   **세부 작업 내역**:
    - **색상 체계 개편**: 기존 사이버펑크 Cyan/Violet 색감을 웜 앰버(`#F59E0B`), 골드(`#FCD34D`), 에메랄드 그린(`#10B981`) 및 다크 웜 옵시디언 톤으로 전량 교체.
    - **골드 스파크 배경 이펙트**: 매트릭스 글리프 코드 비 배경을 은은하게 떠오르는 골드 스파크 파티클 애니메이션으로 전면 개편.
    - **품격 있는 Serif 서체 주입**: 대시보드 헤더 및 주요 카드 영역에 세리프체(`Georgia, 'Times New Roman', serif`)를 적용하여 힐링 브랜드 무드 형성.
    - **백엔드 AuthorityStateManager 복원**: 누락되었던 핵심 상태 관리자 클래스와 `evaluate` 메서드를 명세서에 맞게 안전하게 복구하여 라우터의 `ImportError` 해결.
    - **테스트 케이스 & 라이브러리 연동 버그 해소**:
        - `test_suite.py`의 mock_data 내 `KeyError: 'kpi'` 해결 및 `AuthorityClient` 파라미터 전달 버그 정정.
        - HTTPX `AsyncClient`를 단일 컨텍스트 매니저로 재구축하여 Client Reopen `RuntimeError` 해결.
        - 비동기 테스트 수집을 위한 `@pytest.mark.anyio` 주입 및 HTTPX 0.20+ 대응을 위한 `ASGITransport` 호출 변경.
        - `authority_router.py`에 `response_model_exclude_none=True`를 주입하여 `warning_details`가 `None`일 때 직렬화에서 배제되도록 함으로써 `test_authority_router.py` 오류 해결.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 빌드 완료 (esbuild 60ms 소요).
    - **백엔드 통합 테스트**: `python -m pytest` 실행 시 총 **61개 핵심 모듈 통합 테스트 100% Perfect Green 통과 완료** (61 passed).

---

## 🤖 9. AI 자동 지식 구조화 엔진 (Auto-Gardener) 구현 (2026-06-12 적용 완료)

로컬 LLM을 기반으로 주입된 날것의 지식(Raw Note)을 스스로 분류, 요약, 병합하여 4대 위키 폴더(`💡 Topics`, `⚖️ Decisions`, `🛠️ Projects`, `🚀 Skills`)로 분할 정리해 주는 자율 구조화 백그라운드 엔진을 이식했습니다.

*   **수정 파일**:
    - VS Code 설정 추가: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 엔진 및 브릿지 연동: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
*   **세부 작업 내역**:
    - **설정 추가**: `autoGardenerEnabled`(자동 구조화 토글) 및 `autoGardenerModel`(구조화 전용 경량 모델 지정 옵션) 설정 반영.
    - **AI 구조화 프롬프트 설계**: 주입된 마크다운을 분석해 위키 분할, 고유 제목 작명(안 A 적용), 노드 간의 `[[위키링크]]` 자동 생성 지시 프롬프트 탑재.
    - **스마트 자율 병합(LLM Merge)**: 이미 동일 명칭의 위키 파일이 존재할 경우 기존 파일의 맥락을 살려 새로운 사실만 보태는 누적식 병합 프롬프트 구축.
    - **비동기 UX 구현**: 지식 주입 API 응답에 딜레이를 주지 않고 즉각 성공을 반환한 뒤 3초 후 백그라운드 스레드에서 백그라운드 프로그레스(`vscode.window.withProgress`) 연동 실행.
    - **원격 동기화(Git Sync)**: 구조화가 완료되면 `provider.broadcastGraphRefresh` 및 `_safeGitAutoSync`를 순차 실행하여 깃허브 원격에 자율 커밋/푸시 실행.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 성공 (esbuild 69ms 소요, 무오류 번들링 확인).
    - **백엔드 통합 테스트**: `python -m pytest` 성공 (61개 테스트 통과 완료).


## 🧠 10. 로컬 Graph-RAG 및 지식 연결망 강화 (2026-06-14 적용 완료)

사용자의 프롬프트 질문 키워드를 추출하여 `10_Wiki` 폴더 내 마크다운 지식 노드들의 `[[연관개념]]` 위키링크 및 의미적 연관성(co-occurrence)을 BFS 1-hop 탐색으로 추적하고, 관련 본문 텍스트 전체를 LLM Context에 자율 주입하는 고도화된 로컬 Graph-RAG 아키텍처를 이식했습니다.

*   **수정 파일**:
    - VS Code 설정 추가: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 핵심 엔진 및 대화 핸들러: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
*   **세부 작업 내역**:
    - **설정 추가**: `connectAiLab.graphRagEnabled` 설정을 통해 사용자 기호에 따른 Graph-RAG 활성화 제어 기능 탑재 (기본값 `true`).
    - **질문 기반 Graph-RAG 추출부 구현 (`readGraphRagBrainContextForPrompt`)**:
        - 사용자의 질문 프롬프트에서 특수문자를 제거하고 2글자 이상의 핵심 단어를 추출하여 연관 키워드로 획득.
        - `10_Wiki/` 및 최근 14일 이내 생성된 `00_Raw/` 파일들을 돌며 제목, `[[위키링크]]` 엣지, Shared Anchor 엣지를 수집하여 인메모리 Adjacency List(가벼운 로컬 지식 연결망 그래프) 빌드.
        - 매칭 스코어가 가장 높은 상위 3개의 Seed 노드(🎯)를 추출하고, Seed 노드들로부터 1-hop BFS 탐색을 수행하여 의미적으로 연관된 이웃 노드(🔗)들을 식별.
        - 탐색된 모든 노드의 실 마크다운 본문을 `budgetChars` 상한 제한(기본 `8,000자`) 내로 슬라이싱 및 조립하여 LLM의 주입 컨텍스트 구축.
    - **대화 핸들러 연동**:
        - `_handlePrompt` 및 `_handlePromptWithFile`에서 지식 모드가 활성화되어 있고 `graphRagEnabled`가 참인 경우, 해당 Graph-RAG 지식을 LLM의 시스템 프롬프트(BACKGROUND CONTEXT 부근)에 추가 주입하도록 구현 완료.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 성공 (esbuild 72ms 소요, 완벽 번들링 확인).
    - **백엔드 통합 테스트**: `python -m pytest` 성공 (61개 테스트 통과 완료).
    - **백그라운드 독립 검증**: `test_graph_rag.js` 스크립트를 백그라운드 태스크로 작동시켜 질문 키워드로 Seed 노드(🎯)를 골라내고 1-hop BFS 탐색을 거쳐 연결 노드(🔗)의 본문 및 엣지 관계를 정확히 추출하여 주입함을 완벽하게 확인했습니다. (Success)


## 🤝 11. 멀티 에이전트 자율 토론 및 의사결정 합의 시스템 (2026-06-14 적용 완료)

CEO 에이전트(오영범)가 최종 의사결정이 필요한 중요 비즈니스/설계 안건을 감지하거나 사용자가 `/debate` 명령어를 입력할 때, 관련 전문 분야의 에이전트 2명을 자율 소집하여 상호 챌린지 및 크리틱을 진행하고, CEO가 최종 조율한 절충 합의안을 도출해 `_shared/decisions.md`에 자동 누적 기록 및 가상 사무실 화이트보드에 갱신하는 Co-operative Multi-Agent Debate 엔진을 탑재했습니다.

*   **수정 파일**:
    - VS Code 설정 추가: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 핵심 토론 루프 구현: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
*   **세부 작업 내역**:
    - **설정 키 추가**: `connectAiLab.multiAgentDebateEnabled` 활성화 옵션 탑재.
    - **토론 스트리밍 생중계 엔진 (`_streamAgentSpeech`) 구현**:
        - 각 에이전트의 턴이 돌아올 때마다 해당 에이전트의 이름과 고유 이모지를 노출하고, LLM API의 스트림을 실시간 수집해 인용부(`> `) 기호와 매핑 처리하여 채팅창에 실시간 생중계 타이핑 연출.
    - **라운드 테이블 토론 루프 (`_runAgentDebate`) 구현**:
        - **안건 감지 및 선발**: 안건 텍스트의 키워드 빈도를 비교 분석하여 가장 연관성이 높은 전문 에이전트 2인(매치 점수가 낮을 시 기본 `developer`와 `business` 선발)을 자율 소집.
        - **1단계 (기안)**: 각 에이전트가 본인의 전문 분야 관점에서 작성한 1차 제안안을 스트리밍 수집.
        - **2단계 (교차 크리틱)**: 상대방의 제안안을 읽게 하고, 이에 대한 리스크/리소스 현실성/개선점을 챌린지(Challenge)하는 교차 피드백 생성.
        - **3단계 (합의 & 영구 저장)**: CEO 에이전트가 안건 및 에이전트들의 기안/크리틱을 종합 분석하여 구체적 실천 과제(Action Items)가 포함된 최종 합의 의사결정서를 타결.
        - **자동 연동**: 최종 결정서를 `_shared/decisions.md` 하단에 날짜별로 추가 기록하고, 가상 사무실 화이트보드를 `🤝 의사결정 타결 완료: ...` 상태로 동적 갱신 및 Git 자동 백업 연동.
    - **대화 핸들러 연동**:
        - `_handlePrompt` 입구에서 `/debate` 명령을 확인하거나 의사결정, 기획, 비교 등의 성격을 갖는 안건을 감지했을 때, 자동으로 1대1 대화에서 `_runAgentDebate` 흐름으로 안전하게 우회 분기.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 빌드 완료 (esbuild 72ms 완벽 패스).
    - **백엔드 통합 테스트**: `python -m pytest` 실행 결과 총 61개 통합 테스트 케이스 100% Perfect Green 통과 완료.
    - **백그라운드 독립 검증**: `test_agent_debate.js` 스크립트를 작동시켜 안건의 키워드를 기반으로 연관 에이전트(인스타, 작가)를 자율 매칭 선발하고, 최종 의사결정을 `_shared/decisions.md`에 알맞은 포맷으로 영구 누적 기록함을 성공적으로 확인했습니다. (Success)


## 🔧 12. 코드 자율 실행 검증 및 자가 치유(Self-Healing) 파이프라인 (2026-06-14 적용 완료)

에이전트가 자동 생성하는 파이썬(`.py`) 및 Node.js(`.js`) 스크립트 도구의 실행 결과(stdout/stderr)를 감시하여, 오류 발생 시 LLM 피드백 루프를 통해 에러 원인을 스스로 파악 및 수정한 뒤 다시 덮어써 실행하는 자율 자가 교정(Self-Healing) 파이프라인을 이식했습니다.

*   **수정 파일**:
    - VS Code 설정 추가: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 엔진 및 실행 인터셉터: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
*   **세부 작업 내역**:
    - **설정 추가**: `connectAiLab.selfHealingEnabled`(활성화 토글) 및 `connectAiLab.selfHealingMaxAttempts`(최대 재시도 한도, 기본값 `3`) 설정 적용.
    - **실행 결과 가로채기 (인터셉터) 구현**:
        - `_executeActions` 내의 `<run_command>` 셸 실행기에서 `.py`, `.js` 스크립트 실행 명령어이고 exitCode가 0이 아닌 경우에 한해 자가 치유 프로세스 자동 발동.
    - **LLM 피드백 자가 수정 루프 구현**:
        - 에러가 발생한 대상 스크립트 파일명과 실제 콘솔에 출력된 stderr/Stack Trace 에러 내용, 그리고 원본 소스 코드를 조합하여 전용 치유 프롬프트(`systemHealing`)로 LLM을 호출.
        - LLM이 수정한 새로운 순수 코드를 받아 기존 대상 파일에 안전하게 덮어쓴 뒤 다시 셸 실행(`runCommandCaptured`)을 수행하는 루프를 최대 3회 작동하도록 구현.
    - **실시간 중계 및 HUD 동기화**:
        - 에러 발생 즉시 대화창에 `⚠️ [자가 치유 감지]` 알림과 함께 수정 회차(예: `시도 1/3`) 및 재실행 로그를 실시간 릴레이 중계.
        - 가상 사무실 화이트보드를 `🔧 자가 치유 X차 시도...`로 연동 갱신하여 자율 작업 현황을 마스터에게 실시간 피드백함. 성공 시 `✅ 자가 치유 성공`으로 타결 알림 및 최종 정상 코드 출력.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 성공 (esbuild 114ms 소요, 무오류 번들링 확인).
    - **백엔드 통합 테스트**: `python -m pytest` 성공 (61개 테스트 통과 완료).
    - **백그라운드 독립 검증**: `test_self_healing.js` 스크립트를 작동시켜 ZeroDivisionError 예외 에러가 캡처되는 즉시 자가 수정(Self-Healing) 라이프사이클을 발동하고, 수정한 코드를 디스크에 덮어써 재실행에 완벽히 성공(Retry Exit Code 0)함을 검증했습니다. (Success)


## 📊 13. AI 자율 리스크 시뮬레이터 및 몬테카를로 재무 시나리오 생성기 (2026-06-14 적용 완료)

브레인 내의 프로젝트 목표와 의사결정 문서(`decisions.md`)를 분석해 3대 맞춤형 경영 리스크 요인을 자율 식별하고, 200회 이상의 몬테카를로 샘플링 시뮬레이션을 통해 12개월간의 낙관/보통/비관 시나리오 재무 누적 추이를 표로 시각화하며 `finance_simulation.md`에 영구 기록하는 자율 재무 예측 엔진을 완성했습니다.

*   **수정 파일**:
    - VS Code 설정 추가: [package.json](file:///c:/Users/user/AI%20기업두뇌/내%20작업들/ConnectAI/package.json)
    - 핵심 엔진 및 몬테카를로 계산기: [extension.ts](file:///c:/Users/user/AI%20기업두뇌/내%20작업들/ConnectAI/src/extension.ts)
*   **세부 작업 내역**:
    - **설정 옵션 이식**: `connectAiLab.financeSimulationEnabled` 활성화 설정 키 추가.
    - **자율 파라미터 파싱 및 브레인 지식 추정**:
        - 입력 프롬프트 내에 숫자가 명시된 경우 기초 자금과 목표액으로 획득. 누락 시 브레인 지식에서 매출 목표와 자산 현황을 AI 자율 파서(`_analyzeFinanceBaseParameters` 대안 LLM 흐름)를 통해 지능적으로 자동 추정.
    - **맞춤형 리스크 3대 시나리오 분석**:
        - 브레인 decisions.md 및 비즈니스 현황을 LLM에 주입하여 각 비즈니스에 알맞은 3대 핵심 리스크와 확률, 매출/운영비 증감 영향도를 도출.
    - **200회 몬테카를로 샘플링 시뮬레이션 구현**:
        - 매달의 매출/비용에 Random Walk 난수 분포(0.85 ~ 1.15)를 적용하고, 각 리스크 확률에 따른 가상 롤링을 수행하여 12개월 재무 흐름 데이터를 누적 생성.
        - 수집된 200개 결과 패스를 정렬하여 낙관(상위 10%), 보통(평균 50%), 비관(하위 10%) 통계적 예측 추이 산출.
    - **보고서 저장 및 HUD 화이트보드 갱신**:
        - 시나리오별 12개월 누적 재무 흐름 테이블을 스트리밍 렌더링하고, 상세 리포트를 `10_Wiki/⚖️ Decisions/finance_simulation.md`에 자율 작성 및 영구 백업.
        - 시뮬레이션 완료 즉시 가상 사무실 화이트보드를 `📊 재무 시뮬레이션 완료`로 동적 갱신 및 Git 자동 백업 연동.
    - **대화 라우터 연동**:
        - `/simulate` 명령어로 시작하거나 재무 예측, 몬테카를로, 매출 시뮬레이션 등 재무 분석 의도가 확인될 시 `_runFinanceSimulation` 핵심 계산 루프로 자동 분기 처리.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 성공 (esbuild 61ms 소요, 완벽 번들링 확인).
    - **백엔드 통합 테스트**: `python -m pytest` 성공 (61개 테스트 통과 완료).
    - **백그라운드 독립 검증**: `test_finance_simulator.js` 스크립트를 작동시켜 200회 몬테카를로 재무 시나리오 및 낙관/보통/비관 시나리오 정렬, 그리고 `finance_simulation.md` 마크다운 보고서 자동 생성을 완벽히 마쳤으며 통계적 일관성 검증에 성공했습니다. (Success)


## 🧠 14. 에이전트 장기 기억(LTM) 자율 학습 및 회고 루프 (2026-06-15 최종 구현 및 검증 완료)

세션 동안 발생한 모든 작업 이력, 에러 해결(Self-Healing) 사례, 의사결정 내역을 종합하여 자율적으로 회고 및 반성 일지를 작성하고, 이를 에이전트별 장기 기억 파일(`memory.md`)에 누적 보존해 다음 구동 시 시스템 프롬프트에 자동 결합 주입하는 지속 개선형(Self-Improving) 에이전트 아키텍처를 최종 완수했습니다.

*   **수정 및 신규 파일**:
    - VS Code 설정 반영: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 익스텐션 코어 및 회고 엔진: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
    - Headless 검증 스크립트: [test_reflection_headless.js](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/scratch/test_reflection_headless.js)
*   **세부 구현 및 작업 내역**:
    - **설정 옵션 추가**: `connectAiLab.agentReflectionEnabled` 옵션을 활성화하여 장기 기억 피드백 기능 제어 (기본값 `true`).
    - **최하단 장기 기억 프롬프트 결합 (`buildSpecialistPrompt`)**:
        - 기존 에이전트 소개 바로 하단에 주입되던 `memory.md` 지식을 시스템 프롬프트의 **최하단** `[당신의 장기 학습 및 자율 회고 메모리 (이전 실수 교정 내역)]` 블록으로 결합 주입되도록 수정하여 LLM이 가장 최근 컨텍스트로 주의를 기울이게끔 개선했습니다.
    - **자율 회고 엔진 (`_runAgentSelfReflection`) 단계별 구축**:
        - **1단계: 세션 히스토리 & 작업 로그 수집**: 해당 세션 동안 주고받은 `_chatHistory` 대화 로그를 텍스트화하여 명령어 실행, 에러 발생, 자가 치유(Self-Healing) 성공 내역 등을 완벽히 파싱 및 수집합니다.
        - **2단계: 마스터 위키 회고 보고서 생성**: LLM을 구동하여 오늘 세션의 성공 요인, 실패 극복기, 향후 보완점을 종합 분석한 일지를 작성하고 `10_Wiki/⚖️ Decisions/reflections/reflection_YYYY-MM-DD.md`로 영구 저장합니다.
        - **3단계: 에이전트별 장기 기억(memory.md) 업데이트**: 세션에 실제 참여해 업무를 처리한 에이전트를 자동 식별 및 분류하고, 기존의 장기 기억 지식과 새로운 세션의 교훈을 매끄럽게 통합하는 병합 LLM 호출(`GARDENER_MERGE_SYSTEM`과 유사한 전용 병합 프롬프트)을 수행합니다. 컨텍스트 크기 낭비를 예방하기 위해 크기는 **최대 2,000자 이내**로 제한하도록 제약 요약 압축 룰을 설정했습니다.
        - **4단계: HUD 화이트보드 갱신**: 회고가 완료되면 웹뷰에 `updateWhiteboard` 메시지를 송출하여 가상 사무실 HUD의 화이트보드를 `📝 에이전트 자율 회고 완료` 상태로 즉시 업데이트합니다.
    - **대화 핸들러 연동 및 우회 라우팅**:
        - `_handlePrompt` 및 웹뷰 메시지 리스너(`case 'prompt'`) 입구에서 입력이 `/reflect`로 시작하거나 '회고', '세션 종료' 등의 의도가 감지되는 경우 `_runAgentSelfReflection` 비동기 루프로 우회 연동되도록 제어 흐름을 매핑했습니다.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 빌드가 에러 없이 패스되었습니다. (esbuild 무오류 번들링 완료)
    - **백엔드 통합 테스트**: `python -m pytest` 실행 결과 총 61개 통합 테스트 케이스 **100% Perfect Green 통과 완료** (61 passed).
    - **Headless 시뮬레이터 검증**: `test_reflection_headless.js` 독립 검증 스크립트를 통해 세션 로그 수집, 위키 보고서 생성, `memory.md` 병합 요약, HUD 화이트보드 갱신까지 모든 단계가 한 치의 오차도 없이 통과(PASSED)됨을 성공적으로 입증했습니다. (Success)


## 🤝 15. 비동기 멀티 에이전트 자율 워크플로우(DAG) 엔진 및 실배포 가드레일 (2026-06-15 최종 구현 및 검증 완료)

CEO 에이전트가 단독 또는 1대1 협업을 넘어, 복잡한 비즈니스 미션을 자율적으로 분석하고 작업 순서(의존성 그래프)를 결정해 순차/병렬로 수행하는 **비동기 멀티 에이전트 자율 워크플로우(DAG) 엔진**과 텔레그램/외부 API 등 실배포 직전 사용자의 승인을 대기하는 **Human-in-the-Loop 가드레일**을 구현하고 검증했습니다.

*   **수정 및 신규 파일**:
    - VS Code 설정 반영: [package.json](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/package.json)
    - 익스텐션 코어 및 DAG 러너: [extension.ts](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/src/extension.ts)
    - 웹뷰 UI 및 승인 팝업 카드: [sidebar.html](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/assets/webview/sidebar.html)
    - Headless 검증 스크립트: [test_workflow_headless.js](file:///c:/Users/user/AI%20기업%20두뇌/내%20작업들/ConnectAI/scratch/test_workflow_headless.js)
*   **세부 구현 및 작업 내역**:
    - **설정 옵션 추가**: `connectAiLab.multiAgentWorkflowEnabled` 옵션을 활성화하여 DAG 기반 에이전트 자율 협업 파이프라인 기능 제어 (기본값 `true`).
    - **CEO 기반 동적 DAG 계획 생성 (`_generateWorkflowDAG`)**:
        - 사용자가 준 비즈니스 미션을 분석하여 youtube, designer, developer, writer, researcher, secretary 등 기업 내 에이전트들이 협업할 의존성 순서(Directed Acyclic Graph)를 파싱하고 JSON 데이터 구조로 자동 수립합니다.
    - **비동기 노드 실행 및 퀄리티 검수 반려 루프 (`_runAgentWorkflow`)**:
        - DAG 위상 정렬 순서에 맞춰 각 에이전트가 앞선 작업의 산출물을 활용하여 태스크를 수행하도록 실행(`_executeWorkflowNode`)합니다.
        - 후속 검수자 에이전트가 결과물 퀄리티를 100점 만점으로 평가하여 75점 미만 시 반려 피드백과 함께 재수정을 지시합니다. 무한 루프 방지를 위해 최대 반려 회차는 **2회**로 엄격히 제한하고, 3회차에는 경고와 함께 강제 이행하도록 처리했습니다.
    - **실배포 Human-in-the-Loop 가드레일 구현**:
        - telegram, publish, send, deploy 등 실제 배포나 대외 발송과 직결된 태스크를 자동 식별하여 작동을 블로킹하고, vscode webview로 승인 요청 카드(`workflowApprovalRequired`)를 전송합니다.
        - 사용자가 사이드바 UI에서 `승인 (Approve)` 혹은 `반려 (Reject)`를 클릭하면 extension host에 메시지(`approveWorkflowNode`)를 송출해 Promise 대기를 해제하거나 프로세스를 안전하게 즉시 중단합니다.
    - **최종 완료 및 의사결정서(`decisions.md`) 저장**:
        - 워크플로우 완수 시 각 에이전트별 최종 산출물 요약본을 포함한 결과보고서를 `_shared/decisions.md`에 영구 기록하고 가상 사무실 화이트보드를 `🤝 자율 워크플로우 완수` 상태로 즉시 갱신합니다.
    - **채팅창 명령어 및 자연어 의도 라우터 매핑**:
        - 입력 프롬프트가 `/workflow`로 시작하거나 '협업', '워크플로우' 의도를 포함하는 경우 자율 워크플로우 가동 루프로 자동 라우팅되도록 입구를 연동했습니다.
*   **최종 빌드 및 검증 결과**:
    - **익스텐션 컴파일**: `npm run compile` 빌드가 무오류로 esbuild 번들링을 통과했습니다. (Success)
    - **백엔드 통합 테스트**: `python -m pytest` 실행 결과 총 61개 통합 테스트 케이스 **100% Perfect Green 통과 완료** (61 passed).
    - **Headless 시뮬레이터 검증**: `test_workflow_headless.js` 독립 검증 스크립트를 통해 DAG 수립, 에이전트 순차 실행, 에디터의 퀄리티 평가 및 2회 반려 후 재시도 루프 작동, 3회차 강제 통과 처리, 실배포 시 사용자 승인 대기 Promise 차단 및 승인 시 `decisions.md` 결과보고서 영구 백업과 화이트보드 업데이트까지의 자율 협업 파이프라인의 모든 구간이 완벽하게 PASSED 처리됨을 입증했습니다. (Success)

