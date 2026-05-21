from typing import Dict, Any
import math

# --- Constants for Behavioral Economics Weighting ---
# 1. 손실 회피(Loss Aversion): 사람들은 이득보다 손실에 더 민감함 (보통 2배~2.5배)
LOSS_AVERSION_FACTOR = 2.2
# 2. 규제 리스크 가중치: 법적/규제 변수는 가장 치명적이므로 높은 가중치를 부여함.
REGULATORY_WEIGHT = 0.4

def calculate_avoided_loss(transaction_data: Dict[str, Any], regulatory_risk_score: float) -> float:
    """
    주어진 트랜잭션 데이터와 규제 리스크 점수를 기반으로 총 회피 손실액을 계산합니다.
    Loss = (경제적 손실 * 손실회피계수) + (감정적 손실 * 가중치) + (규제 리스크 * 높은가중치)
    """

    # 1. 경제적 손실 분석 (Economic Loss, L_E)
    try:
        transaction_amount = float(transaction_data.get("amount", 0))
        economic_loss = max(0, transaction_amount * (1 - transaction_data.get("recovery_rate", 1)))
    except ValueError:
        print("[WARNING] Invalid amount data provided.")
        economic_loss = 0.0

    # 2. 감정적 손실 분석 (Emotional Loss, L_Em)
    try:
        # '불안', '좌절' 등 정서 변수와 가중치 기반으로 점수를 계산한다고 가정
        emotional_variables = transaction_data.get("emotional", {})
        anxiety_score = emotional_variables.get("anxiety", 0) / 100 # 최대 100점 스케일 가정
        disappointment_score = emotional_variables.get("disappointment", 0) / 100
        
        # 감정적 손실은 변수별 가중치 합산 (예: 불안 > 좌절)
        emotional_loss = (anxiety_score * 0.6 + disappointment_score * 0.4) * 100 # 최대 100점 스케일 가정
    except Exception as e:
        print(f"[WARNING] Error calculating emotional loss: {e}")
        emotional_loss = 0.0

    # 3. 규제 리스크 손실 (Regulatory Loss, L_R)
    # 규제 점수는 이미 스케일링 되어 들어온다고 가정하며, 여기에 가장 높은 가중치를 부여합니다.
    regulatory_loss = regulatory_risk_score * REGULATORY_WEIGHT

    # --- Total Calculation with Behavioral Weighting ---
    
    # 손실 회피 원칙 적용: 모든 손실 요소를 Loss Aversion Factor (2.2)를 곱하여 증폭시킵니다.
    total_calculated_loss = (economic_loss + emotional_loss + regulatory_loss) * LOSS_AVERSION_FACTOR

    return round(max(0, total_calculated_loss), 2)


def calculate_mitigation_strategy(avoided_loss: float, risk_type: str):
    """
    계산된 손실액을 바탕으로 구체적인 해결책(Mitigation Suggestion)의 방향을 제시합니다.
    """
    if avoided_loss < 50:
        return "현재 리스크는 경미한 수준입니다. 데이터 점검 및 정기적 교육 이수가 권장됩니다."
    elif avoided_loss < 300:
        # 중간 레벨의 리스크
        return f"'{risk_type}'에 대한 즉각적인 원인 분석이 필요합니다. 내부 프로세스 감사(Audit)를 통해 데이터 누락 지점을 확인하세요."
    else:
        # 고위험군
        return "🚨 심각한 단계입니다. 전문가의 1:1 컨설팅과 시스템 전반의 근본적 재구축이 필수적입니다. 즉시 행동 계획을 수립해야 합니다."

# Type Hinting for clarity (Good practice)
if __name__ == '__main__':
    print("--- 테스트 코드 실행 (직접 테스트) ---")
    sample_data = {
        "amount": 5000,
        "recovery_rate": 0.8, # 20% 회복 가능성 가정
        "emotional": {"anxiety": 60, "disappointment": 40}
    }
    risk_score = 0.7 # 1.0 만점 스케일
    
    total_loss = calculate_avoided_loss(sample_data, risk_score)
    strategy = calculate_mitigation_strategy(total_loss, "규제 위반")
    
    print(f"계산된 총 회피 손실액: ${total_loss}")
    print(f"추천 완화 전략: {strategy}")