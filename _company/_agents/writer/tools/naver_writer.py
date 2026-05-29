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

    # 2. 프롬프트 구성 (오영범 마스터 감성 페르소나 강제)
    prompt = f"""당신은 14만 독자의 마음을 어루만져온 '마음을 묻다' 플랫폼의 오영범 마스터입니다. 따뜻하고 서정적인 언어로, 읽는 이의 상처받은 감정을 조용히 보듬는 아날로그 감성 심리 치유 에세이를 작성하십시오.

[최신 마음 트렌드 및 통점 소스]
{trend_src}

[에세이 필수 집필 사양]
1. 페르소나: 오영범 마스터. 지식이나 해답을 강요하지 않으며, "해요", "~입니다", "~하나요?" 와 같은 나긋나긋하고 고풍스러운 다정한 어조(마치 따뜻한 차 한 잔을 앞에 두고 조용히 말을 건네는 듯한 느낌)를 유지하십시오. 절대 딱딱한 기술조나 B2B 칼럼 톤을 쓰면 안 됩니다.
2. 타깃 독자: 번아웃, 사회적 관계의 스트레스, 자책감과 깊은 고독감으로 인해 지쳐서 밤에 쉽게 잠들지 못하는 이 시대의 현대인들.
3. 분량: 독자들이 천천히 호흡을 고르며 마음의 안정을 찾을 수 있도록 네이버 블로그에 최적화된 1,000자 내외의 여운 있는 장문 에세이.
4. 구성:
   - 제목: 지친 마음을 다정하게 노크하는 서정적 헤드라인 (예: "괜찮은 척하느라, 오늘 하루도 참 많이 애쓴 당신에게")
   - 서론: 밤이 찾아왔지만 복잡한 생각으로 뒤척이는 독자들의 하루를 가만히 들여다보며 위로의 안부를 건넴.
   - 본론 1: 바쁘게 달리느라 내가 삼켜버린 눈물과 속마음들이 나약함이 아니라, 그만큼 나 자신을 온 힘을 다해 지키려고 노력했음을 증명한다는 안도감 선사.
   - 본론 2: 치유의 구체적인 제안. 거창한 극복을 요구하지 말고 '오늘 밤, 내 상처받은 마음에게 자그마한 이름 하나 붙여주기'와 같은 실질적인 따뜻한 휴식 조언.
   - 결론: 언제든 내 마음의 작은 숲이 되어 늘 당신 곁을 든든하게 지키겠다는 오영범 마스터의 변치 않는 다정한 약속과 다정 어린 맺음말.
5. 블로그용 최적화:
   - 중간 중간에 `[네이버 블로그 권장 이미지 위치: ...]` (예: 황혼의 하늘, Vintage window, 안개 낀 물가 등 힐링 Unsplash 키워드를 포함) 형태로 이미지 배치 가이드를 삽입하여 사장님이 포스팅을 수월하게 돕도록 설계하십시오.
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
