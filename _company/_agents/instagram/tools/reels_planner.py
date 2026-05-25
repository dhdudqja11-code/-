#!/usr/bin/env python3
# version: instagram_v1
"""Reels Planner — designs 15-30s high-converting Instagram Reels / Shorts scripts,
complete with on-screen visual directions, voiceover scripts, and optimized hashtags.
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
ACCOUNT = os.path.join(YOUTUBE_TOOLS_DIR, "youtube_account.json")
SNIPER_REPORT_PATH = os.path.join(YOUTUBE_TOOLS_DIR, "trend_sniper_report.md")
SCRIPTS_DIR = os.path.join(HERE, "reels_scripts")

def _load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

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
    acct = _load(ACCOUNT) if os.path.exists(ACCOUNT) else {}
    ollama_url = (acct.get("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    model = acct.get("MODEL") or ""

    try:
        import requests
    except ImportError:
        print("❌ pip install requests 가 필요합니다.")
        sys.exit(1)

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

    is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
    print(f"🧠 [LLM 추론 중... 엔진: {'LM Studio' if is_lm_studio else 'Ollama'}]")

    if not model:
        try:
            if is_lm_studio:
                base = ollama_url.rstrip('/')
                if not base.endswith('/v1'):
                    base = base + '/v1'
                r = requests.get(f"{base}/models", timeout=5)
                r.raise_for_status()
                models = [m["id"] for m in r.json().get("data", [])]
            else:
                r = requests.get(f"{ollama_url}/api/tags", timeout=5)
                r.raise_for_status()
                models = [m["name"] for m in r.json().get("models", [])]
            if not models:
                model = "mock-model"
            else:
                model = models[0]
        except Exception:
            model = "mock-model"

    # 추론 실행
    try:
        if model == "mock-model":
            script_content = f"""# 📱 [INSTAGRAM REELS SCRIPT] 100% 오프라인 AI 1인 기업의 비밀

본 릴스 대본은 인스타그램 릴스 알고리즘 노출을 극대화하고, 조회수 대비 프로필 방문 전환율을 300% 이상 끌어올리기 위해 정밀 설계된 숏폼 콘텐츠 기획서입니다.

---

## 🎬 1. 숏폼 영상 타임라인 & 대본 (Video Timeline Script)

**총 분량**: 25초 | **비주얼 컨셉**: 미니멀리즘 테크 & 빠른 컷 편집

| 시간 (초) | 화면 연출 (Visual) | 나레이션 & 오디오 (Audio) | 화면 자막 (Caption) |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:03** | 노트북 와이파이 안테나선을 가위로 자르는 연출 (파격적인 1초 훅) | "인터넷 선을 다 뽑아도 돈 벌어다 주는 AI 비서가 있다?" | **인터넷 끄고 굴리는 AI 비서?! 🤫** |
| **00:03 - 00:10** | 인터넷 연결 없음 창이 떠 있는 화면 옆에서 텔레그램 봇이 실시간으로 블로그 글을 써서 보내주는 장면 클로즈업 | "외부 API 먹통 되면 멈추는 불완전한 챗봇은 이제 끝입니다. 100% 로컬 오프라인 회복 가드로 작동하는 자율 에이전트거든요." | **API 먹통에도 끄떡없는 비밀 🛡️** |
| **00:10 - 00:18** | pytest 터미널 화면에서 57개 테스트가 'Green PASSED'로 순식간에 지나가는 코딩 무결성 실증 장면 | "Pydantic v2 가드레일이 데이터를 완벽하게 검증하니까, 단 한 줄의 데이터 손실 리스크도 용납하지 않습니다." | **Expected Loss = 0% 완벽 검증 📈** |
| **00:18 - 00:22** | 스마트폰을 터치하여 텔레그램 5대 이모지 버튼을 원터치 클릭하는 편안한 사장님의 뒷모습 | "이제 사장님은 텔레그램 터치 한 번으로 원격 제어 끝!" | **손가락 하나로 조종하는 1인 기업 🚀** |
| **00:22 - 00:25** | 카메라를 응시하며 프로필 링크를 가리키는 손가락 제스처 및 강력한 문구 팝업 | "지금 당장 댓글에 '비서'라고 입력하시면, 오프라인 1인 기업 구축 PDF 가이드북을 DM으로 즉시 쏴 드립니다!" | **댓글에 [비서] 적으면 가이드북 즉시 전송! 🎁** |

---

## 🏷️ 2. 추천 태그 및 해시태그 패키지 (Hashtags)

릴스 탐색 탭 노출을 타깃팅하는 알고리즘 최적화 해시태그입니다.

```text
#1인기업 #비즈니스자동화 #AI비서 #인스타그램릴스 #릴스마케팅 #개발자트렌드 #코딩독학 #로컬LLM #PydanticV2 #직장인창업 #무자본창업
```
"""
        elif is_lm_studio:
            base = ollama_url.rstrip('/')
            if not base.endswith('/v1'):
                base = base + '/v1'
            r = requests.post(
                f"{base}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "max_tokens": 2048,
                },
                timeout=180,
            )
            r.raise_for_status()
            script_content = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(f"{ollama_url}/api/generate",
                               json={"model": model, "prompt": prompt, "stream": False},
                               timeout=240)
            r.raise_for_status()
            script_content = r.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM 호출 실패: {e}. 모의 릴스 대본 모드로 안전하게 폴백합니다.")
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
