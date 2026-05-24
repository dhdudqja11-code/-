#!/usr/bin/env python3
import os
import sys
import io
import json
import argparse

# Windows cp949 인코딩으로 인한 이모지 출력 에러 방지 (강제 UTF-8 설정)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_PATH = os.path.join(HERE, "..", "..", "..", "..", "mini_roi_risk_scenarios.json")
CONFIG_PATH = os.path.join(HERE, "roi_calculator.json")

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def main():
    parser = argparse.ArgumentParser(description="비즈니스 가치 산출용 실시간 ROI 및 손실 회피 계산기")
    parser.add_argument("--revenue", type=float, help="대상 기업의 연간 매출액 (USD 기준, 예: 1500000)")
    parser.add_argument("--scenario", type=str, help="리스크 시나리오 ID (PII_LEAK, REGULATION_VIOLATION, SYSTEM_DOWNTIME)")
    parser.add_argument("--keyword", type=str, help="시나리오 키워드 매칭을 위한 검색어 (예: compliance, uptime 등)")

    args = parser.parse_args()

    # 1. 설정 및 시나리오 로드
    cfg = load_json(CONFIG_PATH)
    scenarios_data = load_json(SCENARIOS_PATH)
    scenarios = scenarios_data.get("scenarios", [])

    # 2. 파라미터 Fallback 및 기본값 설정
    revenue = args.revenue
    if revenue is None:
        revenue = float(cfg.get("default_annual_revenue", 1000000))

    scenario_id = args.scenario
    if not scenario_id and args.keyword:
        # 키워드 기반 시나리오 매칭
        kw = args.keyword.lower()
        for s in scenarios:
            if any(k in kw for k in s.get("trigger_keywords", [])):
                scenario_id = s.get("id")
                break

    if not scenario_id:
        scenario_id = cfg.get("default_scenario_id", "REGULATION_VIOLATION")

    # 3. 대상 시나리오 매칭
    selected_scenario = None
    for s in scenarios:
        if s.get("id") == scenario_id:
            selected_scenario = s
            break

    if not selected_scenario:
        # 시나리오 매칭 실패 시 첫 번째 시나리오로 fallback
        if scenarios:
            selected_scenario = scenarios[0]
            scenario_id = selected_scenario.get("id")
        else:
            print(json.dumps({
                "status": "error",
                "message": "사용 가능한 리스크 시나리오를 찾을 수 없습니다."
            }, ensure_ascii=False))
            sys.exit(1)

    # 4. 티어드 요금제 매칭 (Basic/Pro/Enterprise)
    tiers = cfg.get("target_revenue_tiers", [])
    selected_tier = None
    for t in sorted(tiers, key=lambda x: x["revenue_max"]):
        if revenue <= t["revenue_max"]:
            selected_tier = t
            break
    if not selected_tier and tiers:
        selected_tier = tiers[-1]

    solution_cost = selected_tier.get("annual_cost", 5000)
    tier_name = selected_tier.get("tier", "Custom")

    # 5. 위험 및 ROI 수치 계산
    loss_comp = selected_scenario.get("loss_components", {})
    initial_fine_rate = loss_comp.get("initial_fine_rate", 0.05)
    regulatory_penalty_factor = loss_comp.get("regulatory_penalty_factor", 1.0)
    remediation_cost_base = loss_comp.get("remediation_cost_base", 1000000.0)
    risk_level = selected_scenario.get("risk_level", 0.8) # 리스크 제거율/완화 비중

    # 잠재 추정 손실액 (Estimated Loss)
    estimated_loss = (revenue * initial_fine_rate * regulatory_penalty_factor) + remediation_cost_base
    # 회피된 손실액 (Avoided Loss)
    avoided_loss = estimated_loss * risk_level
    # 도입 혜택 순 이익 (Net Benefit)
    net_benefit = avoided_loss - solution_cost
    # ROI (%)
    roi = (net_benefit / solution_cost) * 100

    # 6. 마크다운 리포트 자동 작성
    report = f"""### 📊 [ROI 분석 보고서] {selected_scenario.get('name', '리스크 시나리오')}
* **대상 기업 연 매출**: ${revenue:,.2f}
* **요금제 등급 매칭**: `{tier_name}` (연간 솔루션 비용: ${solution_cost:,.2f})

#### ⚠️ 잠재적 재무 손실 분석
* **기본 과징금 및 복구 비용**: ${estimated_loss:,.2f}
* **리스크 가중 노출 점수**: {risk_level * 100}%
* **안티그래비티 솔루션 도입 시 회피 가능한 재무 손실액(Avoided Loss)**: **${avoided_loss:,.2f}**

#### 💰 투자 효율성 (ROI)
* **순 운영 편익 (Net Benefit)**: ${net_benefit:,.2f}
* **투자 가치 효율 (Estimated ROI)**: **{roi:,.1f}%**

> **💡 전략 권고안**: 
> 본 리스크 시나리오는 기업 연 매출 대비 심각한 타격을 줄 수 있는 고위험군 항목입니다. 
> `{tier_name}` 요금제 도입 비용 대비 **{roi:,.1f}%**의 파격적인 재무적 가치가 증명되므로, 
> 즉각적인 솔루션 배포 및 모바일 제어망 연동을 권고합니다.
"""

    result = {
        "status": "ok",
        "company_revenue": revenue,
        "matched_tier": tier_name,
        "solution_cost": solution_cost,
        "scenario_id": scenario_id,
        "scenario_name": selected_scenario.get("name"),
        "metrics": {
            "estimated_loss": estimated_loss,
            "avoided_loss": avoided_loss,
            "net_benefit": net_benefit,
            "roi_percent": roi
        },
        "report_markdown": report
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
