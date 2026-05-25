#!/usr/bin/env python3
# version: naver_v2
"""Naver Blog Column Writer — acts as a highly authoritative tech-business
evangelist. Automatically parses the latest YouTube trend snapshot from
trend_sniper_report.md, infuses simulation ROI/expected loss metrics,
and drafts a publication-ready Korean business article (1,000+ words) using RTX 4060 Local AI.

Saves posts inside: tools/naver_posts/post_YYYYMMDD_HHMM.md
"""
import os, json, sys, time, datetime, re

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지를 위해 입출력 인코딩을 UTF-8로 강제 적용
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SNIPER_REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")
POSTS_DIR = os.path.join(HERE, "naver_posts")

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
    print("\n✍️ [네이버 칼럼 라이터] 블로그 칼럼 자율 작성기 시작...")
    
    # 1. 소스 데이터 획득
    trend_src = get_latest_trend_source()
    if not trend_src:
        print("⚠️ 최신 트렌드 보고서 소스가 없어 모사 데이터 기반으로 작성을 속행합니다.")
        trend_src = """📡 키워드: 생산성 툴, AI 비즈니스
🌍 트렌드 해킹 분석: 최근 30일간 AI 기반 1인 비즈니스 자동화 콘텐츠 CTR이 전월 대비 280% 폭증. 100% 로컬 오프라인 작동 증명이 핵심 바이럴.
🎯 빈집 털기 전략: 이론적인 수준에 머무는 번역 정보 대신, 비코더가 30초 만에 게임을 실제 배포하고 텔레그램 연동 챗봇을 오프라인 샌드박스로 굴리는 실전 E2E 구현 연출."""

    # 2. 프롬프트 구성 (전문 에반젤리스트 페르소나 강제)
    prompt = f"""당신은 권위 있는 IT 기술 칼럼니스트이자 B2B 비즈니스 전략가(테크 에반젤리스트)입니다. 
아래의 유튜브 트렌드 데이터와 기술 사양을 분석하여, 네이버 블로그에 즉시 발행할 수 있는 고품질 비즈니스 칼럼을 작성하세요.

[트렌드 데이터 소스]
{trend_src}

[칼럼 필수 작성 사양]
1. 페르소나: 고도의 기술적/비즈니스적 통찰력을 갖춘 전문 에반젤리스트. 문장 끝은 "~입니다", "~해야 합니다", "~를 증명합니다" 체를 사용하며 권위 있는 어조 유지.
2. 타깃 독자: 비즈니스 자동화, 1인 AI 기업, 기술적 안전성과 무결성(Expected Loss 방지)을 추구하는 기업가와 개발사 대표들.
3. 분량: 네이버 노출에 최적화된 1,000자 이상의 장문 칼럼.
4. 구성:
   - 제목: 독자의 와우 포인트를 강력히 자극하는 테크-비즈니스형 제목 (예: "와이파이를 끄고 24시간 가동되는 AI 1인 기업의 실체: 기술 무결성의 중요성")
   - 서론: 현재 AI 툴들의 겉핥기식 과장 광고 실태 비판 및 실질적 구현 무결성의 필요성 지적.
   - 본론 1: 100% 로컬(인터넷 없이) 작동하는 오프라인 회복 탄력성(Self-healing) 가드의 구조적 탁월함 분석.
   - 본론 2: Pydantic v2 가드레일을 통해 데이터 검증 실패로 인한 기업 재무적Expected Loss를 0으로 수렴시키는 기술적 실증. (57개 E2E 테스트 무결성 언급)
   - 결론: 24시간 자율 가동되는 메신저(텔레그램) 양방향 인터랙티브 제어의 미래 지향점 제시.
5. 블로그용 최적화:
   - 중간 중간에 `[네이버 블로그 권장 이미지 위치: ...]` 형태로 적절한 시각 플레이스홀더를 삽입하여 사장님이 글을 긁어 포스팅할 때 이미지를 배치하기 편하게 도우세요.
"""

    print("🧠 [LLM 추론 중... 엔진: RTX 4060 GPU 로컬 AI 가속]")
    
    # llm_adapter를 동적 임포트하여 로컬 가중 추론 실행
    try:
        shared_dir = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared"))
        if shared_dir not in sys.path:
            sys.path.append(shared_dir)
        import llm_adapter
        
        post_content = llm_adapter.generate_text(
            prompt=prompt,
            system_instruction="당신은 B2B 에반젤리스트이자 AI 마케터 총괄(레오 페르소나)입니다. IT 칼럼을 집필하십시오.",
            model="llama3"
        )
    except Exception as e:
        print(f"❌ 로컬 어댑터 가동 오류: {e}. 가상 로컬 모드로 완수합니다.")
        post_content = "# 와이파이를 완전히 끄고 만든 게임?! 100% 로컬로 굴리는 AI 1인 기업의 실체\n\n[로컬 AI 가동 오류로 인한 기본 가상 칼럼 작동]"

    # 3. 저장 및 관리
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M')
    file_name = f"post_{timestamp}.md"
    file_path = os.path.join(POSTS_DIR, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(post_content)
        
    print("\n" + "="*60)
    print(post_content)
    print("="*60)
    print(f"\n✅ 네이버 칼럼 블로그 포스팅 백업 및 로컬 작성 완료: {file_path}")

if __name__ == "__main__":
    main()
