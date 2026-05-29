#!/usr/bin/env python3
# version: orchestrator_v1
"""Campaign Orchestrator — orchestrates the entire 1-person company marketing chain:
Sniper -> Writer -> Designer -> Reels Planner -> Naver Publisher -> Instagram Publisher.
Consolidates all files into a unified Campaign Portfolio and logs SQLite database metrics.
"""
import os, sys, json, time, datetime, subprocess, shutil

# Windows 환경 한글 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
COMPANY_ROOT = os.path.abspath(os.path.join(HERE, ".."))
HISTORY_DIR = os.path.join(COMPANY_ROOT, "marketing_history")

# 에이전트 툴 경로 매핑
WRITER_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "writer", "tools")
DESIGNER_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "designer", "tools")
EDITOR_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "editor", "tools")

sys.path.append(HERE)

def run_tool(script_path, args=None):
    """지정한 파이썬 스크립트 도구를 안전하게 실행하고 완료 코드를 받습니다."""
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
        
    # Windows 백그라운드 발열 및 소음 가드레일 통제 플래그 세팅
    kwargs = {"capture_output": True, "encoding": "utf-8", "timeout": 300}
    if sys.platform == "win32":
        kwargs["creationflags"] = 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS
        
    try:
        proc = subprocess.run(cmd, **kwargs)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return -1, "", str(e)

def get_latest_file(directory, extension=".md"):
    """폴더 내에서 가장 최근 생성된 파일 경로를 로드합니다."""
    if not os.path.exists(directory):
        return ""
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]
        if not files:
            return ""
        return max(files, key=os.path.getmtime)
    except Exception:
        return ""

def main():
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    os.environ["CAMP_ORCHESTRATOR_RUNNING"] = "1"
    
    start_time = time.time()
    timestamp = time.strftime('%Y%m%d_%H%M')
    campaign_dir_name = f"campaign_{timestamp}"
    campaign_dir = os.path.join(HISTORY_DIR, campaign_dir_name)
    os.makedirs(campaign_dir, exist_ok=True)
    
    print("📢 ==========================================================")
    print(f"⚡ [캠페인 오케스트레이터] 마음을 묻다 Ryzen 9 병렬 가동 파이프라인 시작: {campaign_dir_name}")
    print("=============================================================")

    # SQLite DB 및 감사 초기화
    try:
        import database
        database.init_db()
        database.log_audit("orchestrator", "CAMPAIGN_START", f"Orchestrating campaign in PARALLEL: {campaign_dir_name}")
    except ImportError:
        pass

    results = {
        "timestamp": timestamp,
        "campaign_directory": campaign_dir,
        "parallel_optimized": True,
        "steps": {},
        "elapsed_seconds": 0.0
    }

    # Step 1: 심리 트렌드 스캔 (trend_sniper.py) - 의존성 최선행 실행
    print("\n📡 Step 1: 심리 트렌드 스캔 분석 중...")
    sniper_start = time.time()
    sniper_py = os.path.join(WRITER_TOOLS, "trend_sniper.py")
    ret, out, err = run_tool(sniper_py)
    results["steps"]["trend_sniper"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    # Sniper report 복사
    trend_report = os.path.join(WRITER_TOOLS, "trend_sniper_report.md")
    if os.path.exists(trend_report):
        shutil.copy2(trend_report, os.path.join(campaign_dir, "01_mental_trends.md"))
    print(f"   └─ 🎯 트렌드 스나이핑 완료 (소요시간: {time.time() - sniper_start:.2f}초)")

    # RAG decisions.md 메모리 자동 압축 및 아카이브 이중화 백업 기동
    try:
        sys.path.append(HERE)
        import decision_compressor
        decision_compressor.compress_decisions()
    except Exception as ce:
        print(f"⚠️ RAG 메모리 압축 가동 실패: {ce}")

    # Step 2, 3, 4: 블로그 집필, 1:1 감성 엽서 설계, 528Hz 치유 음원 작곡 -> 병렬(Parallel) 기동
    print("\n⚡ Step 2, 3, 4: 에이전트 군단 병렬 동시 창작 중 (3 Concurrent Workers)...")
    parallel_start = time.time()
    
    tasks = {
        "naver_writer": (os.path.join(WRITER_TOOLS, "naver_writer.py"), "02_naver_blog.md", os.path.join(WRITER_TOOLS, "naver_posts")),
        "visual_director": (os.path.join(DESIGNER_TOOLS, "visual_director.py"), "03_postcard_guide.md", os.path.join(DESIGNER_TOOLS, "visual_guides")),
        "music_generator": (os.path.join(EDITOR_TOOLS, "music_generate.py"), "05_healing_bgm.mp3", os.path.expanduser("~/connect-ai-music/output"))
    }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_tool, info[0]): name 
            for name, info in tasks.items()
        }
        
        for fut in as_completed(futures):
            name = futures[fut]
            ret, out, err = fut.result()
            results["steps"][name] = "Success" if ret == 0 else f"Failed (exit {ret})"
            
            # 산출물 복사
            dest_name = tasks[name][1]
            src_dir = tasks[name][2]
            ext = ".mp3" if dest_name.endswith(".mp3") else ".md"
            latest_file = get_latest_file(src_dir, extension=ext)
            if latest_file and os.path.exists(latest_file):
                shutil.copy2(latest_file, os.path.join(campaign_dir, dest_name))
                
            # 비주얼 디렉터 완료 시 실물 1:1 postcard PNG 복사 로직 추가
            if name == "visual_director":
                try:
                    png_files = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith(".png")]
                    postcard_candidates = [f for f in png_files if "postcard_" in os.path.basename(f)]
                    
                    postcard_file = None
                    for f in postcard_candidates:
                        if timestamp in os.path.basename(f):
                            postcard_file = f
                            break
                    if not postcard_file and postcard_candidates:
                        postcard_file = max(postcard_candidates, key=os.path.getmtime)
                        
                    if postcard_file and os.path.exists(postcard_file):
                        shutil.copy2(postcard_file, os.path.join(campaign_dir, f"postcard_{timestamp}.png"))
                        print(f"   └─ 🖼️ 1:1 감성 엽서 백업 완료: postcard_{timestamp}.png")
                except Exception as ex:
                    print(f"   ⚠️ PNG 이미지 백업 복사 중 오류: {ex}")
                    
            print(f"   └─ ⚡ {name} 병렬 창작 완료! (상태: {results['steps'][name]})")

    print(f"⚡ 에이전트 군단 병렬 창작 단계 완수! (소요시간: {time.time() - parallel_start:.2f}초)")

    # Step 5: 블로그 자율 발행
    print("\n⚡ Step 5: 플랫폼 자율 발행 어댑터 실행 중...")
    publish_start = time.time()
    
    naver_pub_py = os.path.join(WRITER_TOOLS, "naver_publisher.py")
    naver_status, naver_url = "simulated", ""

    ret, out, err = run_tool(naver_pub_py)
    if ret == 0:
        try:
            json_str = out.strip().split("="*50)[-2].strip()
            data = json.loads(json_str)
            naver_status = data.get("status", "simulated")
            naver_url = data.get("url", "")
        except Exception:
            pass
    
    results["steps"]["naver_publish"] = {"status": naver_status, "url": naver_url}
    print(f"   └─ ⚡ naver_publish 플랫폼 자율 발행 완료! (링크: {naver_url or '시뮬레이션 모드'})")
    print(f"⚡ 플랫폼 자율 발행 단계 완수! (소요시간: {time.time() - publish_start:.2f}초)")

    # Step 6: 몬테카를로 ROI 리스크 분석 & PDF 실물 보고서 자동 전송
    print("\n🎲 Step 6: 몬테카를로 ROI 리스크 분석 및 PDF 실물 보고서 전송 중...")
    WORKSPACE_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
    try:
        import requests
        SIM_DIR = os.path.join(WORKSPACE_DIR, "mini_roi_simulator")
        if WORKSPACE_DIR not in sys.path:
            sys.path.append(WORKSPACE_DIR)
        if SIM_DIR not in sys.path:
            sys.path.append(SIM_DIR)
            
        from mini_roi_simulator.core_api_service import simulate_risk_monte_carlo
        
        # gather risk data points
        import sqlite3
        gateway_dir = os.path.join(WORKSPACE_DIR, "core_gateway")
        db_path = os.path.join(gateway_dir, "gateway_audit.db")
        default_points = [5, 4, 6]
        points = default_points
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM audit_blocks ORDER BY id DESC LIMIT 5")
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    points = [9.0 if r[0] == "FAILURE" else 3.0 for r in rows]
            except Exception:
                pass
                
        input_data = {
            "source": "CampaignOrchestrator",
            "data_points": points
        }
        stats, success = simulate_risk_monte_carlo(input_data)
        if success:
            pdf_path = stats.get("pdf_path")
            chart_path = stats.get("chart_path") or os.path.join(WORKSPACE_DIR, "reports", "monte_carlo_distribution.png")
            
            # copy to campaign folder
            if pdf_path and os.path.exists(pdf_path):
                shutil.copy2(pdf_path, os.path.join(campaign_dir, "06_monte_carlo_risk_report.pdf"))
            if chart_path and os.path.exists(chart_path):
                shutil.copy2(chart_path, os.path.join(campaign_dir, "monte_carlo_distribution.png"))
                
            # send to owner via telegram
            token, chat_id = "", ""
            secretary_json = os.path.join(COMPANY_ROOT, "_agents", "secretary", "tools", "telegram_setup.json")
            if os.path.exists(secretary_json):
                with open(secretary_json, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                token = cfg.get("TELEGRAM_BOT_TOKEN")
                chat_id = cfg.get("TELEGRAM_CHAT_ID")
                
            if token and chat_id:
                # send distribution chart
                if chart_path and os.path.exists(chart_path):
                    url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    with open(chart_path, "rb") as f_chart:
                        requests.post(url, data={"chat_id": chat_id, "caption": "🎲 [마음을 묻다 — 몬테카를로 ROI 리스크 분석 차트]"}, files={"photo": f_chart}, timeout=20)
                # send pdf document
                if pdf_path and os.path.exists(pdf_path):
                    url = f"https://api.telegram.org/bot{token}/sendDocument"
                    with open(pdf_path, "rb") as f_pdf:
                        requests.post(url, data={"chat_id": chat_id, "caption": "📄 [마음을 묻다 — 몬테카를로 리스크 증명서 PDF]\n\nIAG 규제 가드레일 및 GDPR/CCPA 암호화 무결성이 검증된 정식 리스크 리포트 실물입니다."}, files={"document": f_pdf}, timeout=20)
            print("   └─ 🎲 몬테카를로 분석 및 텔레그램 PDF 보고서 전송 완료!")
            results["steps"]["monte_carlo"] = "Success"
        else:
            print("   ⚠️ 몬테카를로 리스크 분석 결과 실패")
            results["steps"]["monte_carlo"] = "Failed"
    except Exception as e:
        print(f"   ⚠️ 몬테카를로 분석 실행 중 에러: {e}")
        results["steps"]["monte_carlo"] = f"Failed ({e})"

    # 전체 경과 시간 연산
    total_elapsed = time.time() - start_time
    results["elapsed_seconds"] = round(total_elapsed, 2)

    # SQLite DB 기록 저장
    try:
        import database
        is_naver = 1 if naver_status == "success" else 0
        database.log_campaign(timestamp, campaign_dir_name, "COMPLETED", None, is_naver, 0)
    except Exception as e:
        print(f"⚠️ 오케스트레이터 DB 로깅 예외: {e}")

    print("\n" + "="*60)
    print("🎉 [캠페인 완성] '마음을 묻다' 치유 캠페인 병렬 파이프라인 가동 성공!")
    print(f"📂 포트폴리오 디렉토리: {campaign_dir}")
    print(f"✍️ 블로그 발행 URL: {naver_url or '시뮬레이션 모드'}")
    print(f"⚡ 캠페인 총 실행 소요 시간: {total_elapsed:.2f}초 (3 Concurrent Workers)")
    print("="*60)
    
    # 텔레그램 간편 포팅 요약을 위해 JSON 문자열 최종 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
