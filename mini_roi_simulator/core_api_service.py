from typing import Dict, Any, Tuple
import sys
import os

# core_gateway를 path에 추가하여 mini_roi_simulator 모델을 가져옵니다.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CORE_GATEWAY = os.path.join(ROOT, "core_gateway")
if CORE_GATEWAY not in sys.path:
    sys.path.append(CORE_GATEWAY)

try:
    from core_gateway.mini_roi_simulator import SimulationInput, RiskFactor, calculate_mini_roi_loss
except ImportError:
    # Fallback to local import if path is different
    from mini_roi_simulator import SimulationInput, RiskFactor, calculate_mini_roi_loss

def simulate_risk(input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    핵심 비즈니스 위험 시뮬레이터 브릿지 함수.
    Pydantic 모델로 변환하여 core_gateway.mini_roi_simulator 로직을 호출합니다.
    """
    try:
        # 1. 입력 데이터 유효성 검증
        if "data_points" not in input_data:
            raise ValueError("Required parameter 'data_points' cannot be found.")
            
        data_points = input_data.get("data_points")
        if data_points is None:
            raise ValueError("Data points cannot be None.")
            
        # 2. data_points 점수의 평균을 기반으로 impact score 매핑
        avg_score = sum(data_points) / len(data_points) if data_points else 0.0
        
        # 3. Pydantic 모델로 주입
        factors = [
            RiskFactor(activity_name="Dynamic Activity", potential_impact_score=avg_score)
        ]
        sim_input = SimulationInput(
            client_id=input_data.get("source", "UnknownClient"),
            user_role="Developer",
            risk_factors=factors
        )
        
        # 4. 코어 로직 실행
        report, total_loss = calculate_mini_roi_loss(sim_input)
        
        # 5. 결과 구성
        status = "CRITICAL" if total_loss > 10000 else "LOW"
        suggestion = ""
        if status == "CRITICAL":
            suggestion = "즉각적인 규제 준수 감사가 필요합니다."
        else:
            suggestion = "지속적인 모니터링이 권장됩니다."
            
        result = {
            "status": status,
            "total_estimated_loss_usd": total_loss,
            "mitigation_suggestion": suggestion,
            "report": [item.dict() for item in report]
        }
        return result, True
        
    except Exception as e:
        # 에러 구조 반환
        return {
            "status": "ERROR",
            "details": {
                "message": str(e)
            }
        }, False

def simulate_risk_api(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """FastAPI 진입점 게이트웨이를 시뮬레이션하는 스트레스 테스트 헬퍼."""
    result, success = simulate_risk(input_data)
    if not success:
        return {
            "success": False,
            "message": f"Internal Server Error: {result.get('details', {}).get('message')}"
        }
    return {
        "success": True,
        "message": "Simulation successful",
        "data": result
    }

def simulate_risk_monte_carlo(input_data: Dict[str, Any], trials: int = 20000, critical_threshold: float = 15000.0) -> Tuple[Dict[str, Any], bool]:
    """
    몬테카를로 리스크 분석 브릿지 함수.
    20,000회 시나리오 시뮬레이션을 실행하고 보고서(PDF)를 생성합니다.
    """
    try:
        from mini_roi_simulator.monte_carlo import run_monte_carlo_simulation, generate_monte_carlo_pdf
        
        # 입력 데이터 검증 및 몬테카를로 가동
        if "data_points" not in input_data:
            raise ValueError("Required parameter 'data_points' cannot be found.")
            
        data_points = input_data.get("data_points")
        if data_points is None:
            raise ValueError("Data points cannot be None.")
            
        stats = run_monte_carlo_simulation(input_data, trials, critical_threshold)
        pdf_path = generate_monte_carlo_pdf(stats)
        
        result = {
            "status": "CRITICAL" if stats["exceed_prob"] > 30.0 else "LOW",
            "stats": stats,
            "pdf_path": pdf_path,
            "mitigation_suggestion": "즉각적인 컴플라이언스 감사 및 decisions.md RAG 자율 통제를 조치하십시오."
        }
        return result, True
    except Exception as e:
        return {
            "status": "ERROR",
            "details": {
                "message": str(e)
            }
        }, False
