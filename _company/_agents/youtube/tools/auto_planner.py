#!/usr/bin/env python3
"""Auto Planner — runs trend_sniper.py on a fixed interval for a chosen
duration (e.g. overnight). Reads its config from auto_planner.json."""
import os, json, time, datetime, subprocess, sys

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지를 위해 입출력 인코딩을 UTF-8로 강제 적용
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "auto_planner.json")
SNIPER_PATH = os.path.join(HERE, "trend_sniper.py")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 설정 파일을 읽을 수 없어요: {CONFIG_PATH}\n{e}")
        sys.exit(1)

def gather_risk_data_points():
    """gateway_audit.db에서 최근 트랜잭션 상태를 분석하여 몬테카를로용 data_points를 수집합니다."""
    import sqlite3
    gateway_dir = os.path.abspath(os.path.join(HERE, "..", "..", "..", "core_gateway"))
    db_path = os.path.join(gateway_dir, "gateway_audit.db")
    
    default_points = [5, 4, 6]
    if not os.path.exists(db_path):
        return default_points
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM audit_blocks ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return default_points
            
        points = []
        for r in rows:
            status = r[0]
            if status == "FAILURE":
                points.append(9.0)
            else:
                points.append(3.0)
        return points
    except Exception:
        return default_points

def get_current_bankruptcy_risk():
    """몬테카를로 2만 회 시뮬레이터를 백그라운드로 실행하여 최신 파산 확률을 취득합니다."""
    try:
        ROOT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        SIM_DIR = os.path.join(ROOT_DIR, "mini_roi_simulator")
        if SIM_DIR not in sys.path:
            sys.path.append(SIM_DIR)
            
        from mini_roi_simulator.monte_carlo import run_monte_carlo_simulation
        points = gather_risk_data_points()
        input_data = {
            "source": "AutoPlannerDaemon",
            "data_points": points
        }
        stats = run_monte_carlo_simulation(input_data, trials=20000, critical_threshold=15000.0)
        return stats.get("exceed_prob", 0.0)
    except Exception as e:
        print(f"⚠️ [Thermal-Guard] 몬테카를로 시뮬레이션 기동 실패: {e}")
        return 0.0

def push_telegram_alert(message):
    """자율적으로 텔레그램 봇 API를 호출하여 사장님께 실시간 리스크 차단 경보를 푸시합니다."""
    try:
        token, chat = "", ""
        ROOT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        SEC_JSON = os.path.join(ROOT_DIR, "_agents", "secretary", "tools", "telegram_setup.json")
        if os.path.exists(SEC_JSON):
            with open(SEC_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            token = cfg.get("TELEGRAM_BOT_TOKEN", "")
            chat = cfg.get("TELEGRAM_CHAT_ID", "")
            
        if token and chat:
            import requests
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat,
                "text": f"🚨 [Thermal-Guard 긴급 리스크 차단]\n\n{message}"
            }
            requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ [Thermal-Guard] 텔레그램 푸시 알림 실패: {e}")

def main():
    # ❄️ Windows 커널 레벨 BELOW_NORMAL 프로세스 우선순위 클래스 조정 (ctypes 순수 바인딩)
    if sys.platform == "win32":
        try:
            import ctypes
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000) # BELOW_NORMAL_PRIORITY_CLASS
            print("❄️  [Thermal-Guard] auto_planner 데몬 프로세스 Windows 커널 스케줄러 BELOW_NORMAL 조정 완착.")
        except Exception as pe:
            print(f"⚠️ [Thermal-Guard] 우선순위 클래스 조정 실패: {pe}")

    cfg = load_config()
    interval_h = float(cfg.get("INTERVAL_HOURS", 6))  # v2.89.71: 디폴트 6시간 (하루 4번)
    total_h = float(cfg.get("TOTAL_RUN_HOURS", 0))    # v2.89.71: 0 = 무한 (24시간 자율 모드)

    # v2.89.71 — 24시간 자율 모드 본격 지원. TOTAL_RUN_HOURS=0이면 사용자가 멈출 때까지 무한.
    if total_h <= 0:
        print(f"\n🌙 [오토 플래너] 24시간 자율 모드 — {interval_h}시간마다 무한 반복")
        print(f"⚠️  사용자가 중단(Ctrl+C)할 때까지 계속 실행됩니다.")
        print(f"     백그라운드로 돌리려면 터미널에서:")
        print(f"     nohup python3 {os.path.abspath(__file__)} > planner.log 2>&1 &")
    else:
        print(f"\n🚀 [오토 플래너] {total_h}시간 동안 {interval_h}시간마다 트렌드 분석 (제한 모드)")
        print(f"⚠️  종료까지 {total_h}시간 채팅창 점유. Ctrl+C로 중단 가능.")
    print()

    if not os.path.exists(SNIPER_PATH):
        print(f"❌ trend_sniper.py를 찾을 수 없어요: {SNIPER_PATH}")
        sys.exit(1)
        
    # Windows CPU/GPU 쿨링 및 소음 차단용 커널 스케줄러 가드레일 빌드
    win_kwargs = {}
    if sys.platform == "win32":
        win_kwargs["creationflags"] = 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS

    # 첫 실행 전 trend_sniper.py가 정상 동작하는지 빠르게 검증
    print("🔍 trend_sniper.py 첫 회차 검증 중 (~30초)...")
    test_proc = subprocess.run([sys.executable, SNIPER_PATH], capture_output=True, text=True, timeout=300, **win_kwargs)
    if test_proc.returncode != 0:
        print(f"❌ trend_sniper.py 검증 실패 (exit {test_proc.returncode})")
        print("   먼저 trend_sniper.py 단독으로 ▶ 실행해서 설정·키워드·LLM 연결 확인 후 재시도.")
        if test_proc.stderr.strip():
            print("   에러 일부:")
            for line in test_proc.stderr.splitlines()[-5:]:
                print(f"   {line}")
        sys.exit(1)
    print("✅ 검증 완료. 본 루프 시작.\n")

    # 실시간 RAG decisions.md 메모리 자동 압축 및 아카이브 이중화 백업 기동
    try:
        SHARED_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared"))
        if SHARED_DIR not in sys.path:
            sys.path.append(SHARED_DIR)
        import decision_compressor
        decision_compressor.compress_decisions()
    except Exception as ce:
        print(f"⚠️ RAG 메모리 압축 가동 실패: {ce}")
    STATE_PATH = os.path.join(HERE, "planner_state.json")

    def _write_state(status, loop_count, start_ts, elapsed, last_ts, next_ts, bankruptcy_risk=0.0, current_interval=0.0):
        try:
            with open(STATE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "status": status,
                    "loop_count": loop_count,
                    "start_time": start_ts,
                    "elapsed_hours": round(elapsed, 2),
                    "last_run_time": last_ts,
                    "next_run_time": next_ts,
                    "bankruptcy_risk": round(bankruptcy_risk, 1),
                    "current_interval_hours": round(current_interval, 2)
                }, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    start = time.time()
    start_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loop = 0
    _write_state("RUNNING", 0, start_ts, 0.0, "N/A", "계산 중...", 0.0, interval_h)
    
    try:
        while True:
            if total_h > 0 and (time.time() - start > total_h * 3600):
                print("\n☀️ 목표 가동 시간을 채웠어요. 종료합니다.")
                _write_state("COMPLETED", loop, start_ts, (time.time() - start) / 3600, "N/A", "N/A", 0.0, interval_h)
                break
            loop += 1
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elapsed_h = (time.time() - start) / 3600
            
            # 🎲 몬테카를로 파산 리스크 스캔
            risk = get_current_bankruptcy_risk()
            current_interval = interval_h
            
            # 20% 초과 시 실행 주기 2배 연장
            if risk > 20.0:
                current_interval = interval_h * 2
                print(f"⚠️ [Thermal-Guard] 파산 리스크 경고 수준 돌파 ({risk:.1f}% > 20.0%)! 자율적으로 실행 주기를 2배 연장합니다. (적용 주기: {current_interval}시간)")
                
            next_at = datetime.datetime.now() + datetime.timedelta(hours=current_interval)
            next_ts = next_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # 🔒 IAG 규제 가드레일 기동 허용 여부 체크
            allowed = True
            try:
                import requests
                allowed_resp = requests.get("http://127.0.0.1:8000/api/v1/planner/allowed", timeout=5)
                if allowed_resp.status_code == 200:
                    allowed = allowed_resp.json().get("allowed", True)
            except Exception:
                pass
                
            # 50% 초과 시 즉각 락다운
            if risk > 50.0:
                allowed = False
                print(f"🚨 [Thermal-Guard] 파산 리스크 위험 임계값 초과 ({risk:.1f}% > 50.0%)! 자율 오토 플래너 락다운 기동!")
                push_telegram_alert(f"몬테카를로 분석에 따른 파산 리스크가 {risk:.1f}%로 안전 수준(50%)을 초과하여 플래너 가동을 강제 일시정지(PAUSED_RISK) 조치했습니다. 사장님의 2FA OTP 승인을 대기합니다.")
                
            if not allowed:
                paused_status = "PAUSED_RISK" if risk > 50.0 else "PAUSED"
                print(f"🚨 [IAG 가드레일 작동] 게이트웨이 또는 리스크 임계값 잠금이 감지되었습니다! 자율 가동 일시정지({paused_status})...")
                _write_state(paused_status, loop - 1, start_ts, elapsed_h, ts, "2FA OTP 승인 대기 중...", risk, current_interval)
                
                # Suspension Loop
                while not allowed:
                    time.sleep(10)
                    try:
                        allowed_resp = requests.get("http://127.0.0.1:8000/api/v1/planner/allowed", timeout=5)
                        if allowed_resp.status_code == 200:
                            # 2FA 락다운 해제 여부 체크
                            allowed = allowed_resp.json().get("allowed", True)
                        risk = get_current_bankruptcy_risk()
                        if risk <= 50.0 and allowed_resp.json().get("allowed", True):
                            allowed = True
                    except Exception:
                        allowed = False
                print(f"✅ [IAG 가드레일 해제 확인] 사장님 2FA 승인이 완료되었습니다. 자율 기동 복원(RESUMED)!")
                _write_state("RUNNING", loop, start_ts, elapsed_h, ts, next_ts, risk, current_interval)

            print(f"\n[{ts}] 🤖 {loop}회차 트렌드 스나이핑 (가동 {elapsed_h:.1f}시간) [최신 리스크: {risk:.1f}%]")
            _write_state("RUNNING", loop, start_ts, elapsed_h, ts, next_ts, risk, current_interval)
            
            try:
                subprocess.run([sys.executable, SNIPER_PATH], check=False, **win_kwargs)
                
                # 실시간 RAG decisions.md 메모리 자동 압축 및 아카이브 이중화 백업 기동
                try:
                    decision_compressor.compress_decisions()
                except Exception as ce:
                    print(f"⚠️ RAG 메모리 압축 가동 실패: {ce}")
            except Exception as e:
                print(f"❌ 실행 실패: {e}")
            
            print(f"⏳ 다음 실행: {next_at.strftime('%Y-%m-%d %H:%M')} ({current_interval}시간 후)")
            time.sleep(current_interval * 3600)
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 수동 종료되었습니다.")
        _write_state("STOPPED", loop, start_ts, (time.time() - start) / 3600, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "N/A", 0.0, interval_h)


if __name__ == "__main__":
    main()
