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

def main():
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
    # 첫 실행 전 trend_sniper.py가 정상 동작하는지 빠르게 검증
    print("🔍 trend_sniper.py 첫 회차 검증 중 (~30초)...")
    test_proc = subprocess.run([sys.executable, SNIPER_PATH], capture_output=True, text=True, timeout=300)
    if test_proc.returncode != 0:
        print(f"❌ trend_sniper.py 검증 실패 (exit {test_proc.returncode})")
        print("   먼저 trend_sniper.py 단독으로 ▶ 실행해서 설정·키워드·LLM 연결 확인 후 재시도.")
        if test_proc.stderr.strip():
            print("   에러 일부:")
            for line in test_proc.stderr.splitlines()[-5:]:
                print(f"   {line}")
        sys.exit(1)
    print("✅ 검증 완료. 본 루프 시작.\n")
    STATE_PATH = os.path.join(HERE, "planner_state.json")

    def _write_state(status, loop_count, start_ts, elapsed, last_ts, next_ts):
        try:
            with open(STATE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "status": status,
                    "loop_count": loop_count,
                    "start_time": start_ts,
                    "elapsed_hours": round(elapsed, 2),
                    "last_run_time": last_ts,
                    "next_run_time": next_ts
                }, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    start = time.time()
    start_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loop = 0
    _write_state("RUNNING", 0, start_ts, 0.0, "N/A", "계산 중...")
    
    try:
        while True:
            # v2.89.71 — total_h = 0이면 무한 (24시간 자율 모드)
            if total_h > 0 and (time.time() - start > total_h * 3600):
                print("\n☀️ 목표 가동 시간을 채웠어요. 종료합니다.")
                _write_state("COMPLETED", loop, start_ts, (time.time() - start) / 3600, "N/A", "N/A")
                break
            loop += 1
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elapsed_h = (time.time() - start) / 3600
            next_at = datetime.datetime.now() + datetime.timedelta(hours=interval_h)
            next_ts = next_at.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n[{ts}] 🤖 {loop}회차 트렌드 스나이핑 (가동 {elapsed_h:.1f}시간)")
            _write_state("RUNNING", loop, start_ts, elapsed_h, ts, next_ts)
            
            try:
                subprocess.run([sys.executable, SNIPER_PATH], check=False)
            except Exception as e:
                print(f"❌ 실행 실패: {e}")
            
            print(f"⏳ 다음 실행: {next_at.strftime('%Y-%m-%d %H:%M')} ({interval_h}시간 후)")
            time.sleep(interval_h * 3600)
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 수동 종료되었습니다.")
        _write_state("STOPPED", loop, start_ts, (time.time() - start) / 3600, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "N/A")


if __name__ == "__main__":
    main()
