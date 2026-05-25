import os
import logging
from typing import Dict, Any

# 로깅 설정: 모든 단계와 예외를 기록하기 위함
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] [%(asctime)s] %(message)s')

def load_environment_config(file_path: str = "config/settings.json") -> Dict[str, Any]:
    """환경 설정 및 API 키를 로드하고 검증합니다."""
    logging.info("--- [STEP 1: Configuration Load Start] ---")
    try:
        # 실제 파일 경로와 구조에 맞춰 수정 필요
        with open(file_path, 'r') as f:
            config = eval(f.read()) # 안전하지 않지만 임시로 사용
            logging.info("✅ Configuration loaded successfully.")
            return config
    except FileNotFoundError:
        logging.error(f"❌ FATAL ERROR: Config file not found at {file_path}.")
        raise EnvironmentError("Config file missing.")
    except Exception as e:
        logging.error(f"❌ FATAL ERROR during configuration parsing: {e}")
        raise RuntimeError(f"Failed to parse config: {e}")

def preprocess_input_data(raw_data: str) -> Dict[str, Any]:
    """입력 데이터를 LLM 호출에 적합한 구조로 전처리합니다."""
    logging.info("--- [STEP 2: Data Preprocessing Start] ---")
    try:
        # 실제 로직을 대체함
        if not raw_data or len(raw_data) < 10:
            raise ValueError("Input data is too short or empty.")
        
        processed = {
            "query": f"Analyze the following trend data for risk assessment: {raw_data[:50]}...",
            "context": "The client's industry and regulatory framework are key considerations."
        }
        logging.info("✅ Data preprocessing completed successfully.")
        return processed
    except Exception as e:
        logging.error(f"❌ ERROR during data preprocessing: {e}")
        raise

def call_llm_api(params: Dict[str, Any]) -> str:
    """LLM API를 호출하고 결과를 받습니다. 이 부분이 핵심 로직입니다."""
    logging.info("--- [STEP 3: LLM API Call Start] ---")
    try:
        # 실제 LLM 클라이언트 초기화 및 호출 코드가 여기에 들어갑니다.
        if not os.getenv("LLM_API_KEY"):
             raise ValueError("Environment variable LLM_API_KEY is not set.")

        logging.warning("⚠️ Mocking LLM API call for diagnostic purposes...")
        # 실제 실패가 발생하던 지점을 모방하여, 설정 오류를 유도해봅니다.
        if params['query'].startswith("Analyze the following trend data"):
             return "Mocked successful analysis result: High risk detected in Q2 regulatory compliance."
        else:
             raise ConnectionError("LLM API endpoint unreachable or invalid parameters.")

    except ValueError as e:
        logging.error(f"❌ LLM Call Logic Error (Parameter/Env): {e}")
        raise
    except Exception as e:
        logging.critical(f"🚨 UNHANDLED CRITICAL ERROR during API call: {type(e).__name__} - {str(e)}")
        # 실패 원인 분석을 위해 스택 트레이스를 출력하는 것이 좋습니다.
        import traceback
        logging.critical("--- Traceback Dump ---")
        logging.critical(traceback.format_exc())
        raise

def run_diagnostic_workflow(raw_input: str):
    """전체 워크플로우를 실행하고 각 단계의 성공/실패를 보고합니다."""
    logging.info("=============================================")
    logging.info("🚀 Starting Trend Sniper Diagnostic Workflow v1")
    logging.info("=============================================")

    try:
        # 1. 환경 로드 검증
        config = load_environment_config()
        print(f"Loaded Config Keys (for verification): {list(config.keys())}") # Key 목록만 출력하여 보안 유지
        
        # 2. 데이터 전처리 검증
        processed_data = preprocess_input_data(raw_input)

        # 3. LLM 호출 검증
        final_result = call_llm_api(processed_data)
        
        logging.info("=============================================")
        logging.info("✅ DIAGNOSTIC SUCCESS: All steps passed.")
        logging.info(f"Final Result: {final_result}")

    except (EnvironmentError, RuntimeError, ValueError, ConnectionError) as e:
        logging.error("\n=============================================")
        logging.error(f"🛑 DIAGNOSIS FAILED at a specific stage: {e.__class__.__name__}.")
        logging.error("=============================================")

if __name__ == "__main__":
    # 테스트할 가상의 입력 데이터
    test_data = "Source A data points 2024-Q1 to 2025-Q2, showing a sharp increase in compliance gaps."
    run_diagnostic_workflow(test_data)