import random
from typing import Dict, Any

def run_monte_carlo_simulation(input_data: Dict[str, Any], trials: int = 20000, critical_threshold: float = 15000.0) -> Dict[str, Any]:
    """
    입력된 data_points를 기반으로 몬테카를로 2만 회 시뮬레이션을 수행하여,
    임계값(critical_threshold)을 초과하는 리스크 확률(exceed_prob)을 계산합니다.
    """
    data_points = input_data.get("data_points", [5, 4, 6])
    if not data_points:
        data_points = [5, 4, 6]
        
    avg_base = sum(data_points) / len(data_points)
    
    exceed_count = 0
    total_losses = []
    
    # 일관성 있는 난수 생성
    random.seed(42)
    
    for _ in range(trials):
        # 정규분포 모사를 위한 간단한 가우스 노이즈
        # random.gauss(1.0, 0.35)
        multiplier = random.gauss(1.0, 0.35)
        loss = avg_base * 3000 * max(0.1, multiplier)
        total_losses.append(loss)
        if loss > critical_threshold:
            exceed_count += 1
            
    exceed_prob = (exceed_count / trials) * 100.0
    mean_loss = sum(total_losses) / trials
    max_loss = max(total_losses)
    
    return {
        "exceed_prob": exceed_prob,
        "mean_loss": mean_loss,
        "max_loss": max_loss,
        "trials": trials,
        "critical_threshold": critical_threshold
    }
