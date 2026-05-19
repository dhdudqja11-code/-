from pydantic import BaseModel, Field
from typing import List, Dict
import datetime

class RiskReport(BaseModel):
    source: str = Field(description="위험 데이터의 출처 (예: SEC Filing, HIPAA Guideline).")
    verification_time: datetime.datetime = Field(description="데이터 검증 시점.")
    risk_score: float = Field(description="현재 시스템이 감지한 위험 점수 (0.0 ~ 1.0).")
    warning_details: str = Field(description="위험 상세 내용 (필요시).")

class RiskDataService:
    """
    외부 규제 데이터베이스 및 API를 통해 실시간 리스크 데이터를 조회하는 서비스.
    트랜잭션 ID나 도메인 기반으로 검색합니다.
    """
    def get_risk_report(self, transaction_id: str, domain: str) -> List[RiskReport]:
        print(f"--- [RiskDataService] Fetching risk data for {domain} / ID:{transaction_id}...")
        # 실제로는 DB 쿼리 또는 REST API 호출이 발생합니다.

        if "finance" in domain and transaction_id == "TXN12345":
            # 특정 조건에서 위험 데이터 반환 시뮬레이션 (🚨 경고 상황)
            report = RiskReport(
                source="SEC Filing",
                verification_time=datetime.datetime.now(),
                risk_score=0.85, # 높은 점수 부여
                warning_details="최근 금융 규제 강화로 인해 개인 데이터 사용 목적의 명확한 정의가 필수적입니다."
            )
            return [report]
        else:
            # 위험 없음 (🟢 정상 상황)
            report = RiskReport(
                source="Internal Model",
                verification_time=datetime.datetime.now(),
                risk_score=0.15,
                warning_details="현재까지는 규제상 큰 이슈가 감지되지 않았습니다."
            )
            return [report]

risk_data_service = RiskDataService()