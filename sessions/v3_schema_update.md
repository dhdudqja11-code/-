# Authority Data Schema v3.0 업데이트 계획 (Researcher 검토)
## 1. 목표 및 범위
기존 v2.0 스키마에 새롭게 정의된 'AI Bias', 'Data Sovereignty Conflict', 'ESG Risk' 데이터를 통합하여, 시스템의 통제 가능성 증명 범위를 확장합니다.

## 2. 업데이트할 핵심 컴포넌트
*   **API Endpoint:** `POST /api/v1/check_authority` (입력 파라미터 및 처리 로직 확장)
*   **UI Component:** Authority Meter, Compliance Status Bar (새로운 리스크 지표 표시 영역 추가)

## 3. v3.0 통합 데이터 스키마 구조 (JSON 예시)
```json
{
  "status": "COMPLIANT", // 또는 NON_COMPLIANT, WARNING
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "overall_compliance_score": 0.92, // 기존 점수 로직 유지
  "risk_metrics": {
    // A. AI Bias Metric (New)
    "ai_bias_status": {
      "is_biased": false,
      "data_provenance_trace": "Trace_ID_12345", // 추적 ID 필수
      "highest_risk_group": null, // 편향된 특정 그룹 명시
      "bias_score": 0.15, // (0.0에 가까울수록 안전)
      "compliance_evidence": "Proof_of_Training_Dataset_V3" 
    },
    // B. Data Sovereignty Metric (New)
    "sovereignty_status": {
      "is_compliant": true,
      "conflict_detected": false,
      "conflicting_jurisdictions": [], // 충돌하는 법규 목록 예: [China PIPL, EU GDPR]
      "data_flow_path_used": "Anon_Gateway_Singapore", // 우회 경로 명시
      "legal_proof_attached": true 
    },
    // C. ESG Metric (New)
    "esg_risk_status": {
      "is_compliant": true,
      "primary_violation": null, // 예: Carbon Emission Exceedance
      "cso_score": 85, // Corporate Sustainability Score (100점 만점)
      "mitigation_plan_verified": true, // 완화 계획 검증 여부
      "estimated_financial_impact_usd": 1200000 // 정량화된 재무적 영향액
    }
  },
  "summary_report": {
    // ... 기존 요약 정보 유지
  }
}
```

## 4. 개발팀 액션 아이템 (Developer/Coder)
1.  `AuthorityMeter` 컴포넌트의 데이터 수신 로직을 위 스키마에 맞게 확장하고, 각 `risk_metrics` 항목별로 독립적인 경고(Glitch Effect) 출력이 가능하도록 구조화해야 합니다.
2.  특히 **ESG Metric**과 관련된 `estimated_financial_impact_usd` 필드가 들어왔을 때, 이를 기준으로 기존의 재무 리스크 계산 로직을 수정하여 시각적 강조를 해야 합니다.

# 코멘트 (Researcher)
새로운 로드맵 기반의 스키마 업데이트는 매우 필수적인 작업입니다. 이 구조를 바탕으로 코다리님은 API 테스트와 컴포넌트 구현에 집중해주시고, Writer님께서는 이 복잡하고 전문적인 데이터를 일반 사용자가 이해할 수 있도록 매력적이면서도 권위 있는 콘텐츠로 변환하는 작업을 진행해 주시면 좋겠습니다.