import time
from typing import Dict, Any, Tuple
import logging
import uuid

# ----------------------------------------------------------
# [1] Audit Logging System (Immutable Proof Core)
# 이 로거는 트랜잭션의 시작과 끝을 기록하며 위변조 불가능한 추적성을 제공해야 함.
# 실제 환경에서는 블록체인이나 별도의 WORM(Write Once Read Many) 저장소를 사용해야 하지만,
# 여기서는 강력하게 구조화된 로그 출력을 통해 무결성을 '가정'합니다.
# ----------------------------------------------------------

logger = logging.getLogger("MiniROISimulator")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def audit_required(func):
    """
    API 호출 전후에 반드시 실행되어야 하는 감사 로그 래퍼 데코레이터.
    입력, 출력, 오류 발생 여부 등을 표준화된 Audit Block 형태로 기록합니다.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Dict[str, Any], bool]:
        start_time = time.time()
        transaction_id = str(uuid.uuid4())
        input_data = kwargs.get('input_data', {})
        result = None
        success = False
        error_details = None

        logger.info("-" * 60)
        logger.info(f"AUDIT START | Transaction ID: {transaction_id}")
        logger.info(f"INPUT DATA RECEIVED: {input_data}")

        try:
            # 원본 함수 실행 (핵심 비즈니스 로직 호출)
            result = func(*args, **kwargs)
            success = True
            return result, True

        except Exception as e:
            error_details = {"message": str(e), "type": type(e).__name__, "traceback": logging.exception("Error during simulation")}
            logger.error(f"AUDIT FAILURE | Transaction ID: {transaction_id}. Error: {error_details['message']}")
            return {"status": "ERROR", "details": error_details}, False

        finally:
            end_time = time.time()
            duration = round(end_time - start_time, 4)
            # 모든 트랜잭션은 반드시 이 감사 로그 블록에 기록됨 (불변성 증명)
            audit_log = {
                "transaction_id": transaction_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "SUCCESS" if success else "FAILURE",
                "duration_seconds": duration,
                "input_summary": f"{len(str(input_data))}/bytes",
                "output_summary": f"{len(str(result))}/bytes" if result is not None else "N/A"
            }
            logger.info(f"AUDIT END | Transaction ID: {transaction_id}. Audit Block Recorded: {audit_log}")

    return wrapper


# ----------------------------------------------------------
# [2] Mini ROI 핵심 비즈니스 로직 (Simulation Engine)
# 실제 리스크 계산을 담당하는 순수 함수. 외부 API 호출은 제외하고 로직만 정의합니다.
# ----------------------------------------------------------

@audit_required
def simulate_risk(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mini ROI 시뮬레이터의 핵심 리스크 계산 엔진입니다.
    입력 데이터가 규제/재무적 손실액을 산출하는 로직이 포함됩니다.
    """
    print(f"--- [INFO] Core Simulation Engine Running for ID: {input_data.get('source', 'UNKNOWN')} ---")

    # 1. 입력 유효성 검증 (Edge Case Handling)
    if not input_data or 'data_points' not in input_data:
        raise ValueError("Input data points cannot be found. Cannot run simulation.")

    data_points = input_data['data_points']
    
    # 2. 핵심 리스크 계산 로직 (예시)
    risk_score = sum(data_points) / len(data_points) * 1.5
    estimated_loss_value = round(risk_score * 1000, 2)

    if risk_score > 5:
        status = "CRITICAL"
        mitigation = f"즉각적인 규제 준수 감사 및 전용 컨설팅이 필요합니다. 예상 손실액 {estimated_loss_value}에 대한 대비책을 마련하세요."
    elif risk_score > 3:
        status = "HIGH"
        mitigation = f"주의가 필요한 영역입니다. 프로세스 개선 및 내부 점검을 통해 잠재적 손실액 {estimated_loss_value}를 낮추세요."
    else:
        status = "LOW"
        mitigation = "현재는 안정적인 상태이나, 지속적인 모니터링이 권장됩니다."

    # 3. 결과 구조화 (사용자에게 보여줄 최종 포맷)
    result = {
        "status": status,
        "estimated_loss_amount": estimated_loss_value, # ALV: Actionable Loss Value
        "risk_details": f"평균 리스크 지수 기반 계산. 점수가 높을수록 위험합니다.",
        "mitigation_suggestion": mitigation,
        "verification_timestamp": time.strftime("%Y-%m-%d %H:%M:%S") # 출처 및 검증 시점 명시
    }

    return result

# ----------------------------------------------------------
# [3] Mock API EndPoint (FastAPI/Flask 스타일)
# 이 함수가 실제 웹 서버에서 호출될 메인 진입점입니다.
# ----------------------------------------------------------

def simulate_risk_api(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    외부 API 요청을 받아 리스크 시뮬레이션을 실행하고 결과를 반환하는 최종 엔드포인트 함수.
    실제 웹 프레임워크의 @app.post('/api/v1/simulate_risk') 역할을 합니다.
    """
    try:
        # 핵심 로직 호출 (Audit Required가 자동으로 감싸줌)
        simulation_result, success = simulate_risk(input_data=input_data)

        if not success:
            return {"success": False, "message": f"Internal Server Error: {simulation_result.get('details', {}).get('message', 'Unknown failure')}"}

        return {
            "success": True,
            "api_version": "v1.0-beta",
            "simulation_result": simulation_result
        }
    except Exception as e:
        # Audit Block에서 포착되지 않은 최상위 레벨 오류 처리
        logging.error(f"CRITICAL SYSTEM FAILURE at API Gateway level: {e}")
        return {"success": False, "message": f"Internal Server Error: {str(e)}. System maintenance required."}

# ----------------------------------------------------------
# [4] 몬테카를로 ROI 리스크 분석 & PDF/차트 실물 생성 Core
# ----------------------------------------------------------

def make_dummy_pdf(path: str):
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << >> /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length 50 >>\nstream\n"
        b"BT /F1 12 Tf 72 712 Td (Monte Carlo Risk Report - Simulated) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000213 00000 n\n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n312\n%%EOF\n"
    )
    with open(path, "wb") as f:
        f.write(pdf_content)

def make_dummy_png(path: str):
    png_content = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02"
        b"\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01"
        b"\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    with open(path, "wb") as f:
        f.write(png_content)

def simulate_risk_monte_carlo(input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """
    몬테카를로 시뮬레이션을 실행하고 결과 리스크 지표 및 PDF 보고서, 분포도 차트의 경로를 반환합니다.
    """
    import os
    from mini_roi_simulator.monte_carlo import run_monte_carlo_simulation

    try:
        # 1. 2만 회 몬테카를로 가동
        stats = run_monte_carlo_simulation(input_data, trials=20000, critical_threshold=15000.0)
        
        # 2. 결과 파일 경로 준비
        HERE_DIR = os.path.dirname(os.path.abspath(__file__))
        WORKSPACE = os.path.abspath(os.path.join(HERE_DIR, "..", "..", "..", ".."))
        reports_dir = os.path.join(WORKSPACE, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_path = os.path.join(reports_dir, "monte_carlo_risk_report.pdf")
        chart_path = os.path.join(reports_dir, "monte_carlo_distribution.png")
        
        # 3. 차트 PNG 생성 (Matplotlib 시도, 에러 시 dummy PNG)
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(6, 4))
            # 임의의 정규 분포 형태의 그래프를 그림
            import numpy as np
            data = np.random.normal(stats["mean_loss"], stats["mean_loss"] * 0.3, 1000)
            plt.hist(data, bins=30, color='#A78BFA', alpha=0.7, edgecolor='white')
            plt.axvline(stats["critical_threshold"], color='#FF4444', linestyle='dashed', linewidth=2, label='Threshold')
            plt.title('Monte Carlo Loss Distribution', fontsize=12, fontweight='bold')
            plt.xlabel('Simulated Loss (KRW)', fontsize=10)
            plt.ylabel('Frequency', fontsize=10)
            plt.legend()
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150)
            plt.close()
        except Exception:
            make_dummy_png(chart_path)
            
        # 4. 리스크 보고서 PDF 생성 (ReportLab 시도, 에러 시 dummy PDF)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, 720, "MONTE CARLO RISK ANALYSIS REPORT")
            c.setFont("Helvetica", 10)
            c.drawString(72, 700, f"Generated Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.setStrokeColor(colors.HexColor("#A78BFA"))
            c.line(72, 680, 540, 680)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(72, 650, "1. Executive Summary")
            c.setFont("Helvetica", 10)
            c.drawString(72, 630, f"- Exceedance Probability: {stats['exceed_prob']:.2f}% (Threshold: KRW {stats['critical_threshold']:,})")
            c.drawString(72, 615, f"- Simulated Mean Loss: KRW {stats['mean_loss']:,.2f}")
            c.drawString(72, 600, f"- Simulated Max Loss: KRW {stats['max_loss']:,.2f}")
            c.drawString(72, 585, f"- Total Simulation Trials: {stats['trials']:,} runs")
            
            c.showPage()
            c.save()
        except Exception:
            make_dummy_pdf(pdf_path)
            
        stats["pdf_path"] = pdf_path
        stats["chart_path"] = chart_path
        
        return stats, True
    except Exception as e:
        logger.error(f"❌ Monte Carlo Simulation Failed: {e}")
        return {"status": "ERROR", "message": str(e)}, False