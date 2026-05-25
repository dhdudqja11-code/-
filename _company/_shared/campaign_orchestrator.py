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
    try:
        proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=300)
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
    timestamp = time.strftime('%Y%m%d_%H%M')
    campaign_dir_name = f"campaign_{timestamp}"
    campaign_dir = os.path.join(HISTORY_DIR, campaign_dir_name)
    os.makedirs(campaign_dir, exist_ok=True)
    
    print("📢 ==========================================================")
    print(f"🚀 [캠페인 오케스트레이터] 신규 일괄 마케팅 체인 기동 완료: {campaign_dir_name}")
    print("=============================================================")

    # SQLite DB 및 감사 초기화
    try:
        import database
        database.init_db()
        database.log_audit("orchestrator", "CAMPAIGN_START", f"Orchestrating campaign: {campaign_dir_name}")
    except ImportError:
        pass

    results = {
        "timestamp": timestamp,
        "campaign_directory": campaign_dir,
        "steps": {}
    }

    # Step 1: YouTube 트렌드 분석 (trend_sniper.py)
    print("\n📡 Step 1: 트렌드 스나이핑 분석 중...")
    sniper_py = os.path.join(YOUTUBE_TOOLS, "trend_sniper.py")
    ret, out, err = run_tool(sniper_py)
    results["steps"]["trend_sniper"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    # Sniper report 복사
    trend_report = os.path.join(YOUTUBE_TOOLS, "trend_sniper_report.md")
    if os.path.exists(trend_report):
        shutil.copy2(trend_report, os.path.join(campaign_dir, "01_youtube_trends.md"))

    # Step 2: 네이버 전문 블로그 글 집필 (naver_writer.py)
    print("✍️ Step 2: 테크 에반젤리스트 칼럼 집필 중...")
    writer_py = os.path.join(YOUTUBE_TOOLS, "naver_writer.py")
    ret, out, err = run_tool(writer_py)
    results["steps"]["naver_writer"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    # 최신 네이버 포스팅 복사
    latest_post = get_latest_file(os.path.join(YOUTUBE_TOOLS, "naver_posts"))
    if latest_post:
        shutil.copy2(latest_post, os.path.join(campaign_dir, "02_naver_blog.md"))

    # Step 3: 비주얼 가이드라인 설계 (visual_director.py)
    print("🎨 Step 3: 프리미엄 썸네일/비주얼 가이드 설계 중...")
    director_py = os.path.join(DESIGNER_TOOLS, "visual_director.py")
    ret, out, err = run_tool(director_py)
    results["steps"]["visual_director"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    latest_guide = get_latest_file(os.path.join(DESIGNER_TOOLS, "visual_guides"))
    if latest_guide:
        shutil.copy2(latest_guide, os.path.join(campaign_dir, "03_visual_guide.md"))

    # Step 4: 인스타그램 릴스 대본 기획 (reels_planner.py)
    print("📱 Step 4: 릴스/쇼츠 숏폼 대본 기획 중...")
    planner_py = os.path.join(INSTAGRAM_TOOLS, "reels_planner.py")
    ret, out, err = run_tool(planner_py)
    results["steps"]["reels_planner"] = "Success" if ret == 0 else f"Failed (exit {ret})"
    
    latest_script = get_latest_file(os.path.join(INSTAGRAM_TOOLS, "reels_scripts"))
    if latest_script:
        shutil.copy2(latest_script, os.path.join(campaign_dir, "04_reels_script.md"))

    # Step 5: 네이버 블로그 자율/시뮬레이션 발행 (naver_publisher.py)
    print("🚀 Step 5: 네이버 블로그 발행 어댑터 실행 중...")
    naver_pub_py = os.path.join(YOUTUBE_TOOLS, "naver_publisher.py")
    ret, out, err = run_tool(naver_pub_py)
    naver_status = "simulated"
    naver_url = ""
    if ret == 0:
        try:
            # JSON 응답 파싱 시도 (마지막 JSON 블록 추출)
            json_str = out.strip().split("="*50)[-2].strip()
            data = json.loads(json_str)
            naver_status = data.get("status", "simulated")
            naver_url = data.get("url", "")
        except Exception:
            pass
    results["steps"]["naver_publish"] = {"status": naver_status, "url": naver_url}

    # Step 6: 인스타그램 릴스 자율/시뮬레이션 발행 (instagram_publisher.py)
    print("🚀 Step 6: 인스타그램 Reels 발행 어댑터 실행 중...")
    insta_pub_py = os.path.join(INSTAGRAM_TOOLS, "instagram_publisher.py")
    ret, out, err = run_tool(insta_pub_py)
    insta_status = "simulated"
    insta_url = ""
    if ret == 0:
        try:
            json_str = out.strip().split("="*50)[-2].strip()
            data = json.loads(json_str)
            insta_status = data.get("status", "simulated")
            insta_url = data.get("url", "")
        except Exception:
            pass
    results["steps"]["instagram_publish"] = {"status": insta_status, "url": insta_url}

    # SQLite DB 기록 저장
    try:
        import database
        is_naver = 1 if naver_status == "success" else 0
        is_insta = 1 if insta_status == "success" else 0
        database.log_campaign(timestamp, campaign_dir_name, "COMPLETED", None, is_naver, is_insta)
    except Exception as e:
        print(f"⚠️ 오케스트레이터 DB 로깅 예외: {e}")

    print("\n" + "="*60)
    print("🎉 [캠페인 완성] 일괄 마케팅 협업 파이프라인 연동 성공!")
    print(f"📂 포트폴리오 디렉토리: {campaign_dir}")
    print(f"✍️ 블로그 발행 URL: {naver_url or '시뮬레이션 모드'}")
    print(f"📱 인스타 발행 URL: {insta_url or '시뮬레이션 모드'}")
    print("="*60)
    
    # 텔레그램 간편 포팅 요약을 위해 JSON 문자열 최종 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
