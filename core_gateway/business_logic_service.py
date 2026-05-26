from typing import Dict, Any
import time
from datetime import datetime

# 가상의 외부 데이터 소스 및 리스크 검증 API (실제로는 HTTP 호출)
MOCK_REGULATORY_RISK_DATA = {
    "GDPR": {"severity": "High", "last_verified": "2026-05-26T10:00:00", "source": "EU Data Council"},
    "HIPAA": {"severity": "Medium", "last_verified": "2026-05-26T09:30:00", "source": "HHS Guidelines"}
}

class BusinessLogicService:
    """
    핵심 비즈니스 로직을 수행하는 서비스 레이어. 
    규제 위험 분석 및 시뮬레이션을 담당합니다.
    """

    def __init__(self, current_user_id: str):
        self.current_user_id = current_user_id
        print(f"[{datetime.now()}] BusinessLogicService initialized for User ID: {current_user_id}")

    async def generate_risk_analysis(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Webhook으로 들어온 트랜잭션 데이터와 외부 규제 위험 데이터를 결합하여 
        [문제 정의 → 원인 분석 → 해결책 제시]의 구조로 리스크 보고서를 생성합니다.
        
        Args:
            transaction_data (dict): Webhook으로 수신된 트랜잭션 정보 {source, time}.

        Returns:
            dict: 표준화된 위험 분석 결과 딕셔너리.
        """
        # 1. 규제 데이터 검색 및 리스크 체크
        risk_report = {"alert": False, "details": []}
        
        # 예시로 GDPR과 HIPAA 두 가지를 검사한다고 가정
        for rule_name, data in MOCK_REGULATORY_RISK_DATA.items():
            if transaction_data.get("source") == "External" and risk_report["alert"] is False:
                # 트랜잭션 데이터와 규제 위험 데이터를 비교하는 로직 (핵심)
                is_critical = data['severity'] == "High" and self._check_violation(transaction_data, rule_name)
                
                if is_critical:
                    report = {
                        "problem_definition": f"Critical Violation Detected: 트랜잭션이 '{rule_name}' 규정을 위반했을 가능성이 높습니다.",
                        "cause_analysis": (
                            f"규제명: {rule_name}. 출처: {data['source']}, 검증 시점: {data['last_verified']}.\n"
                            f"-> 트랜잭션 데이터 ({transaction_data.get('source')}, {transaction_data.get('time')})가 규제 초과 임계치를 감지했습니다."
                        ),
                        "mitigation_suggestion": "즉시 트랜잭션을 중단하고, 관련 부서의 법률 검토를 거쳐 데이터 보존 정책을 재수립해야 합니다. 추가적인 암호화 계층 도입을 권장합니다.",
                    }
                    report["details"].append(report)
                    risk_report["alert"] = True

        # 2. 최종 결과 구성 (성공/실패 여부에 따른 구조적 분리)
        if risk_report["alert"]:
            return {
                "status": "SECURITY ALERT",
                "is_risky": True,
                "analysis_structure": report["details"][0] # 가장 심각한 리스크만 대표로 반환
            }
        else:
            return {
                "status": "CLEAN",
                "is_risky": False,
                "message": "모든 규제 체크를 통과했습니다. 법적 무결성이 확보된 트랜잭션으로 판단됩니다."
            }

    def _check_violation(self, transaction: Dict[str, Any], rule: str) -> bool:
        """내부 검증 헬퍼 함수 (시뮬레이션)."""
        # 실제 복잡한 로직이 들어갈 자리. 여기서는 임의로 True를 반환하여 경고가 발생하도록 시뮬레이션합니다.
        return transaction["source"] == "External" and rule == "GDPR"

    async def execute_core_business_process(self, data: Dict[str, Any]) -> str:
        """
        일반적인 비즈니스 로직 실행 (예: 리스크 검증 후 데이터 처리).
        이 함수를 통해 최종 성공 메시지를 반환합니다.
        """
        result = await self.generate_risk_analysis(data)

        if result["is_risky"]:
            return f"🚨 비즈니스 로직 실패. {result['status']} 감지. 해결책: {result['analysis_structure']['mitigation_suggestion']}"
        else:
            return "✅ 핵심 비즈니스 프로세스가 성공적으로 완료되었으며, 법적 증명력이 확보되었습니다."