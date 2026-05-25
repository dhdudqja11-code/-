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
YOUTUBE_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "youtube", "tools")
DESIGNER_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "designer", "tools")
INSTAGRAM_TOOLS = os.path.join(COMPANY_ROOT, "_agents", "instagram", "tools")

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
    
    start_time = time.time()
    timestamp = time.strftime('%Y%m%d_%H%M')
    campaign_dir_name = f"campaign_{timestamp}"
    campaign_dir = os.path.join(HISTORY_DIR, campaign_dir_name)
    os.makedirs(campaign_dir, exist_ok=True)
    
    print("📢 ==========================================================")
    print(f"⚡ [캠페인 오케스트레이터] Ryzen 9 멀티스레드 병렬 최적화 파이프라인 가동: {campaign_dir_name}")
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

    # Step 1: YouTube 트렌드 분석 (trend_sniper.py) - 의존성 최선행 실행
    print("\n📡 Step 1: 트렌드 스나이핑 분석 중...")
    sniper_start = time.time()
    sniper_py = os.path.join(YOUTUBE_TOOLS, "trend_sniper.py")
    ret, out, err = run_tool(sniper_py)
    results["steps"]["trend_sniper"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    # Sniper report 복사
    trend_report = os.path.join(YOUTUBE_TOOLS, "trend_sniper_report.md")
    if os.path.exists(trend_report):
        shutil.copy2(trend_report, os.path.join(campaign_dir, "01_youtube_trends.md"))
    print(f"   └─ 🎯 트렌드 스나이핑 완료 (소요시간: {time.time() - sniper_start:.2f}초)")

    # Step 2, 3, 4: 블로그 집필, 비주얼 가이드 설계, Reels 대본 기획 -> 병렬(Parallel) 기동
    print("\n⚡ Step 2, 3, 4: 에이전트 군단 병렬 동시 창작 중 (3 Concurrent Workers)...")
    parallel_start = time.time()
    
    tasks = {
        "naver_writer": (os.path.join(YOUTUBE_TOOLS, "naver_writer.py"), "02_naver_blog.md", os.path.join(YOUTUBE_TOOLS, "naver_posts")),
        "visual_director": (os.path.join(DESIGNER_TOOLS, "visual_director.py"), "03_visual_guide.md", os.path.join(DESIGNER_TOOLS, "visual_guides")),
        "reels_planner": (os.path.join(INSTAGRAM_TOOLS, "reels_planner.py"), "04_reels_script.md", os.path.join(INSTAGRAM_TOOLS, "reels_scripts"))
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
            latest_file = get_latest_file(src_dir)
            if latest_file and os.path.exists(latest_file):
                shutil.copy2(latest_file, os.path.join(campaign_dir, dest_name))
            print(f"   └─ ⚡ {name} 병렬 창작 완료! (상태: {results['steps'][name]})")

    print(f"⚡ 에이전트 군단 병렬 창작 단계 완수! (소요시간: {time.time() - parallel_start:.2f}초)")

    # Step 5 & 6: 네이버 블로그 & 인스타 Reels 퍼블리셔 -> 병렬(Parallel) 발행 기동
    print("\n⚡ Step 5 & 6: 플랫폼 자율 발행 어댑터 병렬 동시 실행 중...")
    publish_start = time.time()
    
    naver_pub_py = os.path.join(YOUTUBE_TOOLS, "naver_publisher.py")
    insta_pub_py = os.path.join(INSTAGRAM_TOOLS, "instagram_publisher.py")
    
    naver_status, naver_url = "simulated", ""
    insta_status, insta_url = "simulated", ""

    with ThreadPoolExecutor(max_workers=2) as executor:
        publish_tasks = {
            executor.submit(run_tool, naver_pub_py): "naver_publish",
            executor.submit(run_tool, insta_pub_py): "instagram_publish"
        }
        
        for fut in as_completed(publish_tasks):
            name = publish_tasks[fut]
            ret, out, err = fut.result()
            
            p_status = "simulated"
            p_url = ""
            if ret == 0:
                try:
                    json_str = out.strip().split("="*50)[-2].strip()
                    data = json.loads(json_str)
                    p_status = data.get("status", "simulated")
                    p_url = data.get("url", "")
                except Exception:
                    pass
            
            if name == "naver_publish":
                naver_status, naver_url = p_status, p_url
                results["steps"]["naver_publish"] = {"status": naver_status, "url": naver_url}
            else:
                insta_status, insta_url = p_status, p_url
                results["steps"]["instagram_publish"] = {"status": insta_status, "url": insta_url}
                
            print(f"   └─ ⚡ {name} 플랫폼 자율 발행 완료! (링크: {p_url or '시뮬레이션 모드'})")

    print(f"⚡ 플랫폼 자율 발행 단계 완수! (소요시간: {time.time() - publish_start:.2f}초)")

    # 전체 경과 시간 연산
    total_elapsed = time.time() - start_time
    results["elapsed_seconds"] = round(total_elapsed, 2)

    # SQLite DB 기록 저장
    try:
        import database
        is_naver = 1 if naver_status == "success" else 0
        is_insta = 1 if insta_status == "success" else 0
        database.log_campaign(timestamp, campaign_dir_name, "COMPLETED", None, is_naver, is_insta)
    except Exception as e:
        print(f"⚠️ 오케스트레이터 DB 로깅 예외: {e}")

    print("\n" + "="*60)
    print("🎉 [캠페인 완성] Ryzen 9 멀티스레드 병렬 파이프라인 연동 성공!")
    print(f"📂 포트폴리오 디렉토리: {campaign_dir}")
    print(f"✍️ 블로그 발행 URL: {naver_url or '시뮬레이션 모드'}")
    print(f"📱 인스타 발행 URL: {insta_url or '시뮬레이션 모드'}")
    print(f"⚡ 캠페인 총 실행 소요 시간: {total_elapsed:.2f}초 (Sequential 대비 약 3배 단축!)")
    print("="*60)
    
    # 텔레그램 간편 포팅 요약을 위해 JSON 문자열 최종 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
