from pydantic import BaseModel, Field, validator
from typing import List, Optional
import decimal # 정밀한 금융 계산을 위해 Decimal 사용 권장

# --- 1. 핵심 입력 모델: Avoided Loss 계산에 필요한 모든 변수를 수집 ---
class ComplianceRisk(BaseModel):
    """규제 준수 리스크 관련 입력 값."""
    applicable_regulation_id: str = Field(..., description="적용되는 규정 ID (예: GDPR Art. 32)")
    severity_score: float = Field(..., ge=1, le=5, description="위반 사유의 심각도 (1~5점)")
    estimated_loss_usd: decimal.Decimal = Field(..., description="최악 시나리오 기준 예상 벌금/손실액 (USD)")

class DataBreachRisk(BaseModel):
    """데이터 유출 리스크 관련 입력 값."""
    leaked_user_count: int = Field(..., ge=1, description="유출된 사용자 수")
    avg_damage_per_user_usd: decimal.Decimal = Field(..., description="개인당 평균 손해배상액 (USD)")
    delay_hours: float = Field(..., ge=0.1, description="사고 대응 지연 시간 (Hour)")

class OperationalRisk(BaseModel):
    """운영 효율성 리스크 관련 입력 값."""
    transaction_volume: int = Field(..., ge=1, description="처리해야 할 총 트랜잭션 볼륨")
    error_rate_percent: float = Field(..., ge=0.1, le=100, description="평균 오류 발생률 (%)")
    labor_cost_per_txn_usd: decimal.Decimal = Field(..., description="수작업당 투입 시간/인력 비용 (USD)")

# --- 2. 게이트웨이의 최종 입력 모델 (모든 에이전트가 이 구조로 데이터를 모아 전송) ---
class AvoidedLossInput(BaseModel):
    """Avoided Loss 계산을 위해 필요한 모든 산업별 리스크 변수 통합."""
    compliance_risk: ComplianceRisk
    data_breach_risk: DataBreachRisk
    operational_risk: OperationalRisk

# --- 3. 게이트웨이의 출력 모델 (API Gateway가 반환하는 표준화된 결과) ---
class LossCalculationResult(BaseModel):
    """최종 계산된 Avoided Loss 값."""
    total_avoided_loss_usd: decimal.Decimal = Field(..., description="총 회피 가능 손실액 ($XXM$)")
    breakdown_details: dict[str, str] = Field(..., description="각 리스크 영역별 상세 기여도 분석 (서사적 설명용)")

class AssuranceIndexResult(BaseModel):
    """솔루션이 제공하는 통제력/신뢰도를 나타내는 지표."""
    assurance_index: float = Field(..., ge=0.0, le=1.0, description="[0.0 ~ 1.0] 솔루션을 통한 통제력 확보 비율 (높을수록 좋음)")
    confidence_score_description: str = Field(..., description="C-Level 대상의 구체적인 '확신' 메시지 요약")

# --- 4. 게이트웨이 최종 응답 모델 ---
class CentralGatewayResponse(BaseModel):
    """API Gateway를 통과한 모든 비즈니스 로직 호출의 표준 응답 구조."""
    status: str = Field("SUCCESS", description="처리 상태 (SUCCESS/FAILURE)")
    calculated_loss: LossCalculationResult
    assurance_index: AssuranceIndexResult

# --- 5. 유효성 검증 예시 (선택적) ---
class GatewayValidator:
    @staticmethod
    def validate_input(data: AvoidedLossInput):
        """입력 데이터의 논리적 일관성을 최종적으로 검사하는 로직 자리."""
        # 예: 만약 Compliance Risk가 너무 높다면, Data Breach Risk도 높은 확률로 연쇄 발생한다는 경고를 띄울 수 있음.
        if data.compliance_risk.severity_score > 4 and data.data_breach_risk.delay_hours > 72:
            return "🚨 WARNING: 규제 위험과 데이터 유출 대응 지연이 동시에 높아, 통합 리스크가 기하급수적으로 증가할 수 있습니다."
        return None