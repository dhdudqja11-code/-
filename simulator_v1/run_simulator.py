import os
import sys
import json
import random
import requests
from datetime import datetime
from content_simulator import ContentSimulator

# Windows 쿨링 가드레일 우선순위 격하 설정
def apply_cooling_guardrail():
    if sys.platform == "win32":
        try:
            import win32process
            import win32api
            # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(0x1F0FFF, True, pid)
            win32process.SetPriorityClass(handle, 0x00004000)
            print(">>> Windows BELOW_NORMAL_PRIORITY_CLASS (0x00004000) Cooling Guardrail Loaded successfully!")
        except Exception as e:
            # win32api 가 없을 경우 ctypes를 사용한 폴백
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetCurrentProcess()
                # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
                kernel32.SetPriorityClass(handle, 0x00004000)
                print(">>> Windows BELOW_NORMAL_PRIORITY_CLASS (ctypes fallback) Cooling Guardrail Loaded successfully!")
            except Exception as ex:
                print(f">>> Failed to set process priority: {ex}")

# 텔레그램 알림 설정
TELEGRAM_BOT_TOKEN = "8729092796:AAG9YSMusBSoPh95-QgxC_tqhaPmi97dosA"
TELEGRAM_CHAT_ID = "8834036171"

def send_telegram_simulation_briefing(result, report):
    """
    시뮬레이션 완료 브리핑 카드를 텔레그램으로 전송
    """
    today_str = datetime.now().strftime('%Y-%m-%d')
    decision_korean = {
        "upload_go": "🟢 발행 승인 (Upload Go)",
        "revision_needed": "⚠️ 보완 필요 (Revision Needed)",
        "discard": "❌ 폐기 권고 (Discard)"
    }.get(result['decision'], result['decision'])

    # 채널별 예상 매출 요약
    channel_summary = []
    for ch, data in result.get('channels', {}).items():
        rev = data.get('channel_revenue', 0)
        channel_summary.append(f"• *{ch.upper()}*: `KRW {rev:,}`")

    message_lines = [
        "🌿 *[마음을 묻다] 콘텐츠 시뮬레이션 브리핑* 💌",
        "━━━━━━━━━━━━━━━━━━",
        f"📅 *분석 일자*: `{today_str}`",
        f"📈 *종합 판정*: *{decision_korean}*",
        f"⭐️ *콘텐츠 평점*: `{report['average_score']} / 100` 점",
        f"⚠️ *스팸 리스크*: `{report['spam_risk']} / 100` 점",
        "━━━━━━━━━━━━━━━━━━",
        "💰 *채널별 예상 매출 시뮬레이션*",
        "\n".join(channel_summary) if channel_summary else "• 시뮬레이션 매출 없음 (폐기)",
        f"💵 *총 예상 일일 매출*: `KRW {result.get('total_predicted_revenue', 0):,}`",
        "━━━━━━━━━━━━━━━━━━",
        "💡 _대표님의 치유 철학이 올바른 비즈니스 궤도로 연결되도록 시뮬레이션을 완료했습니다._"
    ]
    
    full_message = "\n".join(message_lines)
    
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(telegram_url, json=payload, timeout=10)
        if response.status_code == 200:
            print(">>> [SUCCESS] Telegram Simulation Briefing sent successfully!")
            return True
        else:
            print(f">>> [FAIL] Telegram API error (Code {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f">>> [ERROR] Exception occurred during telegram sending: {e}")
        return False

def update_metrics_and_states(workspace_dir, average_score, result):
    """
    company_state.json 및 config.json 의 메트릭스를 안전하게 갱신
    """
    state_path = os.path.join(workspace_dir, 'company_state.json')
    config_path = os.path.join(workspace_dir, 'simulator_v1', 'config.json')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 1. company_state.json 갱신
    company_state = {}
    if os.path.exists(state_path):
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                company_state = json.load(f)
        except Exception:
            pass

    company_state['tasksCompleted'] = company_state.get('tasksCompleted', 91)
    company_state['knowledgeInjected'] = company_state.get('knowledgeInjected', 0)
    company_state['lastSessionDate'] = today_str
    
    # 시뮬레이터 구동 메트릭스 업데이트
    company_state['simulationRuns'] = company_state.get('simulationRuns', 0) + 1
    company_state['contentEvaluated'] = company_state.get('contentEvaluated', 0) + 1
    if result.get('decision') == 'discard':
        company_state['predictionsCorrected'] = company_state.get('predictionsCorrected', 0) + 1
        
    try:
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(company_state, f, ensure_ascii=False, indent=2)
        print(">>> [SUCCESS] company_state.json metrics updated successfully.")
    except Exception as e:
        print(f"Error writing company_state.json: {e}")

    # 2. config.json 갱신
    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            pass
            
    if 'metrics' not in config_data:
        config_data['metrics'] = {}
        
    config_data['metrics']['tasks_completed'] = company_state['tasksCompleted']
    config_data['metrics']['knowledge_injected'] = company_state['knowledgeInjected']
    config_data['metrics']['last_session_date'] = today_str
    config_data['metrics']['simulation_runs'] = company_state['simulationRuns']
    config_data['metrics']['content_evaluated'] = company_state['contentEvaluated']
    config_data['metrics']['predictions_corrected'] = company_state.get('predictionsCorrected', 0)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(">>> [SUCCESS] config.json metrics synchronized successfully.")
    except Exception as e:
        print(f"Error writing config.json: {e}")

def main():
    print("====================================================")
    print(">>> Asking the Heart: Content Simulation Daemon <<<")
    print("====================================================")
    
    apply_cooling_guardrail()
    
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(workspace_dir, 'simulator_v1', 'config.json')
    
    # 1. 시뮬레이터 인스턴스화
    simulator = ContentSimulator(config_path)
    
    # 2. 무작위 또는 사용자 지정 후보군 생성
    # 기본 모의 평가 데이터 조제
    mock_content_candidates = [
        {
            "hooking_score": 88,
            "empathy_score": 92,
            "sales_connection": 85,
            "seo_score": 75,
            "cta_score": 82,
            "spam_risk": 15
        },
        {
            "hooking_score": 95,
            "empathy_score": 60,
            "sales_connection": 90,
            "seo_score": 85,
            "cta_score": 90,
            "spam_risk": 55
        },
        {
            "hooking_score": 72,
            "empathy_score": 78,
            "sales_connection": 68,
            "seo_score": 70,
            "cta_score": 65,
            "spam_risk": 35
        }
    ]
    
    # 무작위로 후보 선택하여 시뮬레이션 가동
    selected_candidate = random.choice(mock_content_candidates)
    
    # 아규먼트로 직접 전달받았는지 확인 (수동 테스트 연동 가능)
    if len(sys.argv) > 1:
        try:
            passed_scores = json.loads(sys.argv[1])
            if isinstance(passed_scores, dict):
                selected_candidate = passed_scores
                print(">>> Loaded manual evaluation scores from arguments!")
        except Exception:
            pass

    print(f">>> Selected Content Scores for evaluation: {selected_candidate}")
    
    # 3. 콘텐츠 평가 진행
    decision, avg_score, report = simulator.evaluate_content(selected_candidate)
    print(f">>> [EVALUATION COMPLETE] Decision: {decision.upper()} | Avg Score: {avg_score}")
    
    # 4. 매출 시뮬레이션 가동
    simulation_result = simulator.run_revenue_simulation(decision, selected_candidate)
    print(f">>> [REVENUE SIMULATION COMPLETE] Predicted Revenue: KRW {simulation_result.get('total_predicted_revenue', 0):,}")
    
    # 5. 로컬 데이터베이스 갱신 및 파일 저장
    latest_result_path = os.path.join(workspace_dir, 'simulator_v1', 'simulation_result_latest.json')
    try:
        output_payload = {
            "evaluation_report": report,
            "simulation_result": simulation_result
        }
        with open(latest_result_path, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, ensure_ascii=False, indent=2)
        print(f">>> [SUCCESS] Saved latest simulation result to: {latest_result_path}")
    except Exception as e:
        print(f"Error saving latest simulation result: {e}")
        
    # 6. 메트릭스 및 상태 업데이트
    update_metrics_and_states(workspace_dir, avg_score, simulation_result)
    
    # 7. 텔레그램 연동 채널 브리핑 발송
    if simulation_result['status'] == 'success':
        send_telegram_simulation_briefing(simulation_result, report)
        
    print("====================================================")
    print(">>> Content Simulation Run Completed Successfully! <<<")
    print("====================================================")

if __name__ == '__main__':
    main()
