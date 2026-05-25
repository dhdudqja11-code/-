#!/usr/bin/env python3
# version: instagram_v2
"""Reels Planner — designs 15-30s high-converting Instagram Reels / Shorts scripts,
complete with on-screen visual directions, voiceover scripts, and optimized hashtags
using RTX 4060 Local AI.

Saves scripts inside: tools/reels_scripts/script_YYYYMMDD_HHMM.md
"""
import os, json, sys, time, datetime, re

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
YOUTUBE_TOOLS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "youtube", "tools"))
SNIPER_REPORT_PATH = os.path.join(YOUTUBE_TOOLS_DIR, "trend_sniper_report.md")
SCRIPTS_DIR = os.path.join(HERE, "reels_scripts")

def get_latest_trend_source():
    """trend_sniper_report.md에서 가장 최근의 트렌드 보고서 섹션을 파싱합니다."""
    if not os.path.exists(SNIPER_REPORT_PATH):
        return ""
    try:
        with open(SNIPER_REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        sections = content.split("# 🎯 트렌드 스나이핑 보고서")
        if len(sections) > 1:
            return sections[-1].strip()
    except Exception:
        pass
    return ""

def main():
    print("\n📱 [릴스 플래너] 인스타 숏폼 콘텐츠 기획 시작...")
    
    # 1. 소스 데이터 획득
    trend_src = get_latest_trend_source()
    if not trend_src:
        print("⚠️ 최신 트렌드 보고서 소스가 없어 모사 데이터 기반으로 작성을 속행합니다.")
        trend_src = """📡 키워드: 생산성 툴, AI 비즈니스
🌍 트렌드 해킹 분석: 최근 30일간 AI 기반 1인 비즈니스 자동화 콘텐츠 CTR이 전월 대비 280% 폭증. 100% 로컬 오프라인 작동 증명이 핵심 바이럴.
🎯 빈집 털기 전략: 이론적인 수준에 머무는 번역 정보 대신, 비코더가 30초 만에 게임을 실제 배포하고 텔레그램 연동 챗봇을 오프라인 샌드박스로 굴리는 실전 E2E 구현 연출."""

    # 2. 프롬프트 구성 (인스타그램 마케터 페르소나 강제)
    prompt = f"""당신은 SNS 인플루언서 마케팅을 마스터한 인스타그램 전문 크리에이티브 디렉터입니다.
아래의 트렌드 분석 리포트를 바탕으로, 15~30초 분량의 임팩트 있고 중독적인 인스타 릴스(Instagram Reels) / 유튜브 쇼츠(Shorts) 대본을 작성하세요.

[트렌드 데이터 소스]
{trend_src}

[릴스 대본 필수 작성 사양]
1. 타깃: 1인 기업가, AI 자동화, 코딩 독학 관심자, 퇴사 후 창업을 꿈꾸는 예비 사장님들.
2. 진행 분량: 15~30초 (최대 150단어 내외, 매우 빠르고 펀치력 있는 호흡).
3. 구성 구조:
   - 0~3초 (강력한 훅/Hook): 3초 안에 시선을 붙잡을 파격적인 카피와 화면 구성.
   - 3~25초 (본론): 3~4개의 씬(Scene)으로 분할하여 화면 연출(Visual)과 나레이션/자막(Audio)을 매칭하여 기술.
   - 25~30초 (행동 유도/CTA): "프로필 링크 클릭" 또는 "댓글로 '비법'이라고 적어주시면 PDF를 보내드립니다!" 등 전환율 극대화 전략.
4. 해시태그 패키지: 검색 노출과 릴스 알고리즘에 최적화된 트렌디한 해시태그 7~10개 제공.
"""

    print("🧠 [LLM 추론 중... 엔진: RTX 4060 GPU 로컬 AI 가속]")
    
    # llm_adapter를 동적 임포트하여 로컬 가중 추론 실행
    try:
        shared_dir = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared"))
        if shared_dir not in sys.path:
            sys.path.append(shared_dir)
        import llm_adapter
        
        script_content = llm_adapter.generate_text(
            prompt=prompt,
            system_instruction="당신은 인플루언서 마케팅 대가(인스타그램 크리에이티브 에이전트)입니다. 대본을 완벽히 기획하십시오.",
            model="llama3"
        )
    except Exception as e:
        print(f"❌ 로컬 어댑터 가동 오류: {e}. 가상 로컬 모드로 대본을 빌드합니다.")
        script_content = f"""# 📱 [INSTAGRAM REELS SCRIPT] 100% 오프라인 AI 1인 기업의 비밀 (Fallback)

*   **0~3초**: "와이파이를 완전히 끄고 24시간 일하는 AI 비서가 있다?!"
*   **3~12초**: 인터넷 연결 없이도 로컬 LLM과 연동되어 자율 작동 및 자가 복구.
*   **12~20초**: Pydantic v2와 57개 완벽한 E2E 검증 테스트가 보장하는 데이터 무결성.
*   **20~25초**: 댓글에 '비서'라고 적어주시면 100% 로컬 챗봇 구축 비밀 매뉴얼을 DM으로 즉시 전송!
*   **해시태그**: #1인기업 #비즈니스자동화 #AI마케팅 #로컬LLM
"""

    # 3. 저장 및 관리
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR, exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M')
    file_name = f"script_{timestamp}.md"
    file_path = os.path.join(SCRIPTS_DIR, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_content)
        
    print("\n" + "="*60)
    print(script_content)
    print("="*60)
    print(f"\n✅ 인스타그램 릴스 대본 생성 완료: {file_path}")

if __name__ == "__main__":
    main()
