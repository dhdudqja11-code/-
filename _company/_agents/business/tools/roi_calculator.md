# 📊 `roi_calculator` — 실시간 ROI 및 손실 회피 계산기

이 도구는 대상 기업의 연 매출과 관련 리스크 시나리오를 바탕으로 잠재 재무적 손실(Estimated Loss), 회피 가능 손실(Avoided Loss), 그리고 솔루션 요금제 대비 ROI(투자 가치 효율)를 계량 분석하여 구조화된 JSON 데이터와 마크다운 보고서로 출력합니다.

---

## 🛠️ 입력 파라미터 (Arguments)

CLI 인자로 파라미터를 넘겨 호출합니다:

| 인자명 | 타입 | 설명 | 필수 여부 | 예시 |
|---|---|---|---|---|
| `--revenue` | float | 대상 기업의 연간 매출액 (USD) | 선택 (기본값 $1M) | `--revenue 2500000` |
| `--scenario` | string | 적용할 리스크 시나리오 ID (`PII_LEAK`, `REGULATION_VIOLATION`, `SYSTEM_DOWNTIME`) | 선택 | `--scenario PII_LEAK` |
| `--keyword` | string | 시나리오 매칭용 검색어 (trigger_keywords와 자동 비교) | 선택 | `--keyword compliance` |

---

## 📊 시나리오 정보

*   **`PII_LEAK` (개인정보 유출)**: 개인정보 유출에 따른 과징금 및 복구 비용 (기본 완화율: 80%)
*   **`REGULATION_VIOLATION` (규제 위반)**: GDPR 등 법규 위반으로 인한 심각한 규제 비용 (기본 완화율: 95%)
*   **`SYSTEM_DOWNTIME` (시스템 중단)**: 핵심 시스템 다운타임으로 인한 재무 손실 (기본 완화율: 70%)

---

## ⚙️ 요금제 및 도입 비용 (자동 등급 배칭)

대상 기업의 연 매출액에 따라 솔루션 도입 예산이 자동으로 책정됩니다:
*   **Basic 등급**: 연 매출 $500,000 이하 $\to$ 솔루션 연간 비용 **$1,200**
*   **Pro 등급**: 연 매출 $5,000,000 이하 $\to$ 솔루션 연간 비용 **$6,000**
*   **Enterprise 등급**: 연 매출 $5,000,000 초과 $\to$ 솔루션 연간 비용 **$24,000**

---

## 📥 출력 결과 (JSON)

실행 성공 시 다음과 같은 스키마의 JSON이 반환됩니다:
```json
{
  "status": "ok",
  "company_revenue": 1000000.0,
  "matched_tier": "Pro",
  "solution_cost": 6000.0,
  "scenario_id": "REGULATION_VIOLATION",
  "scenario_name": "규제 위반 (Regulatory Violation)",
  "metrics": {
    "estimated_loss": 1300000.0,
    "avoided_loss": 1235000.0,
    "net_benefit": 1229000.0,
    "roi_percent": 20483.333
  },
  "report_markdown": "### 📊 [ROI 분석 보고서] ... (가독성 높은 텍스트 보고서)"
}
```

---

## 💡 에이전트 활용 팁

*   사용자(사장님)가 "A사의 개인정보 유출 시 ROI 좀 계산해봐"라고 요청하면, 즉시 `--revenue <A사매출>`과 `--scenario PII_LEAK`을 조합하여 이 도구를 실행하세요.
*   출력된 `report_markdown`과 `roi_percent` 수치를 복사하여 사장님 보고서와 영숙이(비서)의 텔레그램 승인 메시지 원고로 인계하세요.
