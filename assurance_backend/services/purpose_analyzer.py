from pydantic import BaseModel, Field
from typing import Dict, Any

# 1. 데이터 구조 정의: Purpose Vector는 정형화되어야 합니다.
class PurposeVector(BaseModel):
    primary_intent: str = Field(description="사용자가 가장 중요하게 생각하는 근본적 목적.")
    target_domain: str = Field(description="서비스가 적용될 산업/도메인 (예: Healthcare, Finance).")
    required_assurance_type: str = Field(description="요구되는 핵심 보장 유형 (예: Compliance, Novelty, Stability).")

class PurposeAnalyzerService:
    """
    사용자의 서사적 목적을 분석하여 정형화된 '목적 벡터'를 추출하는 서비스.
    실제로는 LLM API 호출이 발생합니다. 여기서는 Mocking합니다.
    """
    def analyze_purpose(self, user_description: str) -> PurposeVector:
        print("--- [PurposeAnalyzerService] User purpose analysis initiated...")
        if not user_description or len(user_description) < 10:
            raise ValueError("User description is too vague. Cannot generate vector.")

        # 실제 LLM 호출 로직을 여기에 구현합니다 (예: openai.chat.completions.create...)
        # 현재는 임시로 하드코딩된 Mock 데이터를 반환하여 구조 검증에 집중합니다.
        try:
            vector_data = {
                "primary_intent": "규제 준수 및 신뢰 확보",
                "target_domain": "금융 (Finance)",
                "required_assurance_type": "Compliance"
            }
            return PurposeVector(**vector_data)
        except Exception as e:
             print(f"[ERROR] Vector creation failed: {e}")
             raise

# 테스트용 인스턴스를 전역으로 준비합니다.
purpose_analyzer = PurposeAnalyzerService()