# Mini ROI Risk Simulation - UI/UX Design Brief v1.0
## 목표: 기술적 우월성 및 긴급 위기 대응 시스템 인식 심어주기

### 🎯 핵심 경험 (Emotional Journey)
사용자가 데이터 입력 → 로딩(분석 과정) → 충격적인 결과 확인 → 해결책 필요성 인지 순서로 감정 변화를 느끼게 한다.

### 🎨 디자인 시스템
*   **Primary Color:** #007AFF (신뢰, 기술)
*   **Secondary Color:** #CC3333 (위험, 심각도 경고)
*   **Background:** #F5F7FA (전문 보고서 배경)
*   **Typography:** Inter / Pretendard

### 💻 컴포넌트 상세 정의
1. **리스크 등급 게이지 (Risk Grade):**
    - **Critical State:** Deep Red/Black Gradient + Error Code 느낌의 오버레이.
    - **애니메이션:** 로딩 직후, 수치가 급격히 하락하는 애니메이션 적용 필수.
2. **손실액 시각화 (Estimated Loss):**
    - **애니메이션:** Typewriter Effect를 사용하여 숫자를 충격적으로 카운트업.

### 🖱️ 인터랙션 가이드라인
*   **Focus:** 입력 필드 활성화 시 네온 블루 그리드 패턴 효과 적용.
*   **Hover (CTA):** 버튼 하단에 Glow Effect + '🔒' 아이콘 표시.
*   **System Loading:** 로딩 스피너 대신 "SYSTEM PROCESSING... DETECTING ANOMALIES..." 타이핑 메시지 사용.