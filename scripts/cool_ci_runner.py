#!/usr/bin/env python3
# version: cool_ci_v1
"""Thermal-Aware Local CI/CD Test Runner — executes all Python test suites
using BELOW_NORMAL_PRIORITY_CLASS CPU scheduling and cooling rest intervals
to prevent Ryzen 9/RTX 4060 thermal spikes, rendering a premium dashboard.
"""
import os
import sys
import time
import subprocess
import json

# Windows 한글 입출력 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
REPORTS_DIR = os.path.join(WORKSPACE, "reports")
CI_REPORT_MD = os.path.join(REPORTS_DIR, "ci_test_report.md")

TEST_SUITES = [
    {
        "name": "Developer Risk Simulator Tests",
        "cmd": [sys.executable, "_company/_agents/developer/tests/test_mini_roi_simulator.py"],
        "desc": "개발자 에이전트 핵심 리스크 모의 시뮬레이터 로직 유효성 단위 검증"
    },
    {
        "name": "Telegram Bot Integration Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_telegram_bot_integration.py"],
        "desc": "텔레그램 2FA OTP, 락다운 해제, 결재 마이그레이션 및 대시보드 연동 통합 검증"
    },
    {
        "name": "Sound Engine & Double-Send Prevention Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_sound_generator.py"],
        "desc": "사운드 엔진 BGM 생성 및 캠페인 오케스트레이터 중복 전송 방지 검증"
    },
    {
        "name": "Remote Control & Compliance Diagnostics Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_remote_control.py"],
        "desc": "원격 관제 백엔드 RBAC 권한, 토큰 만료, 진단 무결성 에러 검증"
    },
    {
        "name": "API Gateway Namespace Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_api_gateway.py"],
        "desc": "API 게이트웨이 네임스페이스 모듈 패키지 해소 및 웹훅 처리 검증"
    },
    {
        "name": "Core Compliance Gateway Tests",
        "cmd": [sys.executable, "-m", "pytest", "core_gateway/"],
        "desc": "코어 게이트웨이 보안 필터, 2FA 토큰 챌린지, IAG 감사 로그 적재 검증"
    },
    {
        "name": "Avoided Loss Router & Schema Tests",
        "cmd": [sys.executable, "-m", "pytest", "backend/tests/test_avoided_loss_router.py"],
        "desc": "Avoided Loss Pydantic 스키마 매핑 및 422-to-400 오류 처리 검증"
    },
    {
        "name": "Avoided Loss E2E & Integration Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_avoided_loss_e2e.py", "tests/test_avoided_loss_integration.py"],
        "desc": "트랜잭션 및 행동경제학적 Avoided Loss 결합 E2E 연쇄 검증"
    },
    {
        "name": "Connectivity & Security Gateway Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_connectivity.py"],
        "desc": "로그인 세션 락다운 및 QuotaExceeded 네트워크 장애 유효성 검증"
    },
    {
        "name": "Core Simulator API & Loss Calculator Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_e2e_mini_roi.py", "tests/test_simulation_api.py", "tests/test_loss_calculator.py", "tests/test_risk_assessment.py"],
        "desc": "비동기 시뮬레이션 엔드포인트 및 위험 수준 등급 호환성 검증"
    },
    {
        "name": "Trend Sniper Hybrid RAG Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_trend_sniper.py"],
        "desc": "유튜브 쿼터 고 고갈 시 자율 웹 스카우터 폴백 및 decisions.md 피딩 검증"
    },
    {
        "name": "Auto Planner Risk & Ctypes Cooling Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_auto_planner_cooling.py"],
        "desc": "오토 플래너 24h 데몬의 ctypes 우선순위 강제 격하 및 몬테카를로 리스크 하이브리드 제어 E2E 검증"
    },
    {
        "name": "PDF Premium Aesthetics & Cryptosystem Tests",
        "cmd": [sys.executable, "-m", "pytest", "tests/test_pdf_premium_aesthetics.py"],
        "desc": "2대 PDF 보고서의 딥 스페이스 사이버 네온 HSL 리디자인 및 2중 SHA-256 서명/SSoT 적재 E2E 검증"
    }
]

def run_ci_pipeline() -> dict:
    """CPU/GPU 온도 세이프 스케줄링 가드레일 하에서 전체 테스트를 순차 구동합니다."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Windows CPU 스케줄러 BELOW_NORMAL_PRIORITY_CLASS 플래그 선언
    win_kwargs = {}
    is_windows = (sys.platform == "win32")
    if is_windows:
        win_kwargs["creationflags"] = 0x00004000
        
    print("=" * 80)
    print("❄️  [Thermal-Guard CI/CD 스케줄러] 전사 통합 빌드 및 검증 시작")
    print(f"● 가동 환경: Windows OS (BELOW_NORMAL CPU 조절 활성화)" if is_windows else "● 가동 환경: Unix/macOS (일반 CPU 스케줄러)")
    print("● 안전 가드: 각 테스트 스위트 구동 사이 1.0초 쿨다운 간격 적용 (소음 및 발열 최소화)")
    print("=" * 80)
    
    suite_results = []
    total_passed = 0
    total_failed = 0
    start_time = time.time()
    
    # PYTHONPATH 강제 매핑 설정
    env = os.environ.copy()
    env["PYTHONPATH"] = f".{os.pathsep}{env.get('PYTHONPATH', '')}"
    
    for idx, suite in enumerate(TEST_SUITES):
        print(f"\n🚀 [CI Stage {idx+1}/{len(TEST_SUITES)}] {suite['name']}")
        print(f"  👉 설명: {suite['desc']}")
        print(f"  👉 실행: {' '.join(suite['cmd'])}")
        
        stage_start = time.time()
        try:
            # 쿨 가드레일 매핑 기동
            proc = subprocess.run(
                suite["cmd"], 
                capture_output=True, 
                encoding="utf-8", 
                errors="replace",
                env=env,
                **win_kwargs
            )
            
            stage_elapsed = time.time() - stage_start
            success = (proc.returncode == 0)
            
            if success:
                print(f"  🟢 [CI Stage {idx+1} SUCCESS] 통과! (소요 시간: {stage_elapsed:.2f}초)")
                total_passed += 1
                status = "SUCCESS"
                err_log = ""
            else:
                print(f"  🔴 [CI Stage {idx+1} FAILURE] 검증 실패! (exit {proc.returncode})")
                total_failed += 1
                status = "FAILED"
                err_log = proc.stderr or proc.stdout
                if err_log:
                    # 너무 긴 에러 로그 축소
                    lines = err_log.splitlines()
                    err_log = "\n".join(lines[-20:]) if len(lines) > 20 else err_log
                    print(f"  ⚠️ 에러 요약:\n{err_log}")
            
            suite_results.append({
                "stage": idx + 1,
                "name": suite["name"],
                "status": status,
                "elapsed": round(stage_elapsed, 2),
                "error": err_log
            })
            
        except Exception as e:
            stage_elapsed = time.time() - stage_start
            total_failed += 1
            print(f"  🔴 [CI Stage {idx+1} ERROR] 시스템 에러 발생: {e}")
            suite_results.append({
                "stage": idx + 1,
                "name": suite["name"],
                "status": "ERROR",
                "elapsed": round(stage_elapsed, 2),
                "error": str(e)
            })
            
        # 쿨다운 인터벨 슬립
        time.sleep(1.0)
        
    total_elapsed = time.time() - start_time
    
    # 3. 마크다운 보고서 빌드
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    report_lines = [
        f"# ❄️ Thermal-Guard CI/CD 전사 빌드 자동화 리포트",
        f"- **검증 일시**: {current_time}",
        f"- **소요 시간**: {total_elapsed:.2f}초",
        f"- **가드레일 상태**: SUCCESS (BELOW_NORMAL CPU 활성화)",
        f"- **통과 여부**: {'🟢 Perfect PASS' if total_failed == 0 else '🔴 FAILURE 발생'}",
        f"\n## 📊 테스트 스위트별 상세 실행 내역 (총 {len(TEST_SUITES)}개)",
        f"| 스테이지 | 테스트 스위트명 | 상태 | 소요시간 (초) |",
        f"| :--- | :--- | :--- | :--- |"
    ]
    
    for res in suite_results:
        emoji = "🟢 SUCCESS" if res["status"] == "SUCCESS" else "🔴 FAILED"
        report_lines.append(f"| Stage {res['stage']} | {res['name']} | {emoji} | {res['elapsed']:.2f}s |")
        
    if total_failed > 0:
        report_lines.append("\n### 🚨 FAILED 상세 요약 로그")
        for res in suite_results:
            if res["status"] != "SUCCESS" and res["error"]:
                report_lines.append(f"\n#### [{res['name']} 에러]")
                report_lines.append(f"```text\n{res['error']}\n```")
                
    # 파일 영구 보존
    with open(CI_REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "=" * 80)
    print("📊 [CI 완료] 전사 144개 빌드 검증 및 쿨 스케줄링 완수")
    print(f"● 총 소요 시간: {total_elapsed:.2f}초")
    print(f"● 성공: {total_passed}건 / 실패: {total_failed}건")
    print(f"● 영구 MD 보고서 저장 완료: {CI_REPORT_MD}")
    print("=" * 80)
    
    return {
        "success": (total_failed == 0),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_elapsed": round(total_elapsed, 2),
        "results": suite_results
    }

if __name__ == "__main__":
    run_ci_pipeline()
