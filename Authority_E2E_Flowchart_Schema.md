# 🛡️ Authority Score Pre-Assessment: E2E 데모 시나리오 및 기술 스펙

## 📜 개요 (The Narrative Flow)
본 문서는 '마음을 묻다' 서비스의 핵심 가치인 **시스템적 권위(Systemic Authority)**를 사용자에게 체감시키는 전 과정을 구조화한 마케팅용 시나리오이자, 동시에 백엔드 로직을 정의하는 기술 스펙 문서입니다. 사용자가 스스로 자신의 시스템 취약성을 진단하고 '통제권 확보 과정'에 비용을 지불하게 만드는 3단계의 플로우를 명시합니다.

**핵심 원칙:** 단순한 점수 제시가 아닌, **문제 발견 $\rightarrow$ 원인 분석 $\rightarrow$ 해결책 제시 (Authority Warning)**의 구조적 사고 과정을 강제해야 합니다 [근거: 🏢 회사 정체성].

---

## 🚀 I. 시스템 상태 전이 로직 (The State Machine)

**A. IDLE $\to$ WARNING (진단 단계): 위기감 고조 유발**
| 요소 | 설명 | 기술적 트리거/조건 | 출력 메시지 구조 |
| :--- | :--- | :--- | :--- |
| **사용자 경험(UX)** | "당신은 현재 시스템의 잠재적 리스크를 인식하지 못하고 있습니다." (따뜻한 공감 $\rightarrow$ 경고) | $AuthorityScore < Threshold_{Warning}$<br>AND<br>$L_{reg}$ 데이터셋 기반 리스크 미검증 지표 존재 [근거: 💻 코다리 — 검증된 지식] | **[PROBLEM DEFINITION]:** 현재 시스템은 외부 구조적 취약점에 노출되어 있습니다.<br>**[ANALYSIS]:** (예: 특정 지역/규제 A에 대한 데이터 수집 누락) <br>**[SOLUTION SUGGESTION]:** 심화 진단을 통해 $L_{reg}$ 커버리지를 확보해야 합니다. |
| **데이터 흐름(Data Flow)** | 사용자가 입력한 기본 정보와 외부 규제 리스크 데이터셋($L_{reg}$) 간의 불일치점을 비교하여 '위험 점수'를 계산합니다. | `POST /api/v1/check_authority`<br>Request Body: `{ user_data, region, industry }` <br>**처리 로직:** $Score = Min(AuthorityMetrics)$ | **API 응답 스키마 (Warning):** `<Schema Ref: authority_warning>`<br>Status Code: `202 Accepted / Warning` |

**B. WARNING $\to$ CONTROLLED (권위 확보 단계): 전문적 해결책 제시**
| 요소 | 설명 | 기술적 트리거/조건 | 출력 메시지 구조 |
| :--- | :--- | :--- | :--- |
| **사용자 경험(UX)** | "시스템의 취약점을 진단했습니다. 이제 전문가의 도움을 받아 통제권을 확보하십시오." (문제 제기 $\rightarrow$ 해결책 판매) | 사용자가 '심화 진단' 또는 'Authority Package 구매'를 시도함. 시스템이 $L_{reg}$ 데이터셋 중 **결여된 항목**을 성공적으로 매칭하여 Gap Report를 생성할 때. | **[PROBLEM DEFINITION]:** (재확인)<br>**[ANALYSIS]:** 현재 확보 가능한 통제권은 X%입니다.<br>**[SOLUTION SUGGESTION]:** *Authority Package* 구매를 통해 Y 리스크 영역의 증명된 권위(Proof)를 확보할 수 있습니다. |
| **데이터 흐름(Data Flow)** | $L_{reg}$ 데이터셋 중 '결여 항목'을 식별하고, 이 결여 항목에 대한 전문 컨설팅/보고서 구매 프로세스를 시작합니다. | `POST /api/v1/mitigate_risk`<br>Request Body: `{ gap_report_id, package_level }` <br>**처리 로직:** 데이터 검증을 위한 **'권위 증명(Proof)'** 과정 실행 및 비용 산정. | **API 응답 스키마 (Controlled):** `<Schema Ref: authority_controlled>`<br>Status Code: `201 Created / Solution Available` |

---

## ⚙️ II. 기술 명세서: API 데이터 구조 정의 (Schema & Logic)

### 1. Authority Warning Schema (`authority_warning`)
이 스키마는 단순 오류 메시지가 아닌, [문제-원인-해결책]의 논리적 흐름을 강제합니다. 이는 시스템적 권위(Systemic Authority)를 기술적으로 증명하는 핵심입니다.

```json
{
  "status": "WARNING",
  "authority_level": 0.2, // 예: 0.2 (최저치 기반의 리스크 지표)
  "timestamp": "2026-06-15T10:30:00Z",
  "report_id": "WARN-[UUID]",
  "diagnostic_report": {
    "problem_definition": { // 1. 문제 정의 (What went wrong?)
      "title": "시스템 구조적 결함 경고: [규제명 A] 미준수 리스크",
      "description": "현재 운영 환경은 법률 위반 벌금이 아닌, 시스템 아키텍처의 근본적인 취약점에서 발생할 수 있는 위험에 노출되어 있습니다." // [근거: 🏢 회사 정체성]
    },
    "root_cause_analysis": { // 2. 원인 분석 (Why did it go wrong? Source/Time)
      "source_system": "Global Compliance Data Feed",
      "missing_data_type": ["GDPR-Article-17", "CCPA-Right-to-Erase"],
      "risk_level": "High Criticality", // '개인 실수'가 아닌 시스템적 결함으로 포장
      "time_window": { "start": "2023-01-01", "end": "Ongoing" } 
    },
    "mitigation_suggestion": { // 3. 해결책 제시 (How to fix it?)
      "action": "Authority Package 구매 및 데이터 Gap Fill",
      "cost_estimate": "$5,000 - $25,000",
      "recommended_next_step": "심화 컨설팅 요청 -> Proof Generation 시작"
    }
  }
}
```

### 2. Authority Controlled Schema (`authority_controlled`)
시스템이 통제권을 확보했음을 선언하는 응답입니다. '통제' 자체가 판매되는 가치임을 강조합니다.

```json
{
  "status": "CONTROLLED",
  "authority_level": 0.95, // 예: 0.95 (높은 수준의 통제권 확보)
  "timestamp": "2026-06-15T11:00:00Z",
  "proof_id": "CTRL-[UUID]",
  "validation_summary": {
    "overall_status": "Systemic Authority Secured",
    "validated_scope": ["GDPR", "CCPA", "Local Law B"], 
    "compliance_gap_reduction_rate": "95% (Previous: 20%)" // 수치로 권위 증명
  },
  "proof_details": {
    "proof_source": "Client Authority Package (Proof Document)",
    "validated_artifacts": [
      {"name": "Data Flow Map", "status": "Verified"},
      {"name": "Access Control List (ACL)", "status": "Compliant"}
    ]
  }
}
```

---

## 🧪 III. 핵심 기술 검증 및 테스트 시나리오

**테스트 목표:** 모든 상태 전이 지점(IDLE $\to$ WARNING $\to$ CONTROLLED)에서 시스템은 패닉하지 않고, 반드시 **'통제권 재확립 중...'** 이라는 메시지를 출력하며 구조화된 응답을 반환해야 한다. [근거: 💻 코다리 — 검증된 지식]

| 테스트 시나리오 | 발생 상황 (Input) | 기대되는 시스템 반응 로직 | 필수 기술 검증 항목 |
| :--- | :--- | :--- | :--- |
| **1. Network Failure** | 외부 API 게이트웨이 연결 실패(Timeout/503). | 에러 메시지 대신, `[Authority Warning]` 구조의 '통제권 재확립 중...' 상태를 출력하고, 마지막으로 성공했던 $L_{reg}$ 데이터 스냅샷을 제공해야 함. | **회복탄력성 (Resilience):** 롤백 로직 및 Fallback Response 구현 여부. [근거: 💻 코다리 — 검증된 지식] |
| **2. Data Inconsistency** | 사용자가 제출한 데이터와 $L_{reg}$ 데이터셋이 상충함. | IDLE $\to$ WARNING 전이 트리거. 불일치하는 데이터를 원인으로 분석하고, 해당 규정의 *수정/보완 필요성*을 권위적으로 경고해야 함. | **데이터 무결성 (Integrity):** 충돌 데이터에 대한 진단 및 보고서 생성 로직 검증. [근거: 💻 코다리 — 검증된 지식] |

---