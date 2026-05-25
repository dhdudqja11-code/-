#!/usr/bin/env python3
# version: designer_v1
"""Visual Director — plans advanced visual layout guidelines, color palettes,
typography choices, and high-converting thumbnail/banner copies.
Analyzes the latest blog post from naver_writer.py or uses mock trends.

Saves guides inside: tools/visual_guides/guide_YYYYMMDD_HHMM.md
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
NAVER_POSTS_DIR = os.path.join(YOUTUBE_TOOLS_DIR, "naver_posts")
GUIDES_DIR = os.path.join(HERE, "visual_guides")

def _load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_latest_naver_post():
    """naver_posts 폴더에서 가장 최근에 저장된 마크다운 블로그 칼럼을 로드합니다."""
    if not os.path.exists(NAVER_POSTS_DIR):
        return ""
    try:
        files = [os.path.join(NAVER_POSTS_DIR, f) for f in os.listdir(NAVER_POSTS_DIR) if f.endswith(".md")]
        if not files:
            return ""
        latest_file = max(files, key=os.path.getmtime)
        with open(latest_file, "r", encoding="utf-8") as f:
            return f.read()
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

    print("\n🎨 [비주얼 가이드 디렉터] 디자인 기획 시작...")
    
    # 1. 소스 데이터 획득 (최신 네이버 블로그 글 파싱)
    post_src = get_latest_naver_post()
    if not post_src:
        print("⚠️ 최신 네이버 포스팅이 없어 기본 테크 비즈니스 컨셉 기반으로 기획합니다.")
        post_src = """# 와이파이를 완전히 끄고 만든 게임?! 100% 로컬로 굴리는 AI 1인 기업과 기술 무결성의 실체
        오프라인 로컬 가드레일 설계와 Pydantic v2 방어막을 통한 B2B Expected Loss 방지가 중요합니다.
        텔레그램 원터치 조종실로 24시간 양방향 조종을 완성합니다."""

    # 2. 프롬프트 구성 (비주얼 디렉터 페르소나 강제)
    prompt = f"""당신은 세계적인 프리미엄 디자인 에이전시의 수석 비주얼 디렉터입니다.
아래의 마케팅/테크 칼럼 콘텐츠를 분석하여, 이에 가장 잘 어울리는 고품질 썸네일 카피(텍스트), 
색상 팔레트, 레이아웃 구도 및 폰트 매칭 등 프리미엄 디자인 지시서(비주얼 가이드)를 작성하세요.

[칼럼 콘텐츠 소스]
{post_src}

[비주얼 가이드 필수 기획 사양]
1. 비주얼 컨셉: 칼럼의 테마인 '100% 로컬 오프라인', 'Pydantic v2 가드레일', '보안 조종실' 느낌을 살린 미래지향적 테크 프리미엄(Cyber-security + Tech premium).
2. 색상 팔레트: HSL 또는 Hex 컬러 코드가 명시된 3~4개 조화로운 팔레트 제안 (예: Deep Space Black, Cyber Neon Blue, Safety Orange 등).
3. 썸네일 & 배너 카피: 
   - 유튜브/블로그 노출용 극강의 클릭율(CTR)을 보장하는 헤드라인 카피 3가지.
   - 썸네일에 들어갈 서브 텍스트(설명).
4. 레이아웃 & 구도 가이드: 
   - 배경, 주 피사체 배치(예: 사선 레이아웃, 황금 비율 등), 텍스트 레이어 순서 구체적 기술.
5. 타이포그래피 제안: 구글 폰트나 보편적 프리미엄 영문/국문 폰트 조합 제안 (예: Inter + Pretendard, Outfit + 나눔스퀘어 등).
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
            guide_content = f"""# 🎨 [PREMIUM VISUAL GUIDE] 테크 무결성 & 오프라인 AI 1인 기업

본 비주얼 가이드는 최신 마케팅 칼럼을 심도 있게 분석하여, 고도의 기술적 신뢰도와 로컬 오프라인 회복 탄력성을 강력한 시각 이미지로 형상화하기 위해 설계된 프리미엄 지시서입니다.

---

## 🌈 1. 큐레이션 색상 팔레트 (Harmonious Palette)

디자인 테마는 **'Dark-Cyber Security & Trusted Shield'**입니다. 차분하면서도 포인트 컬러가 시선을 잡아끄는 럭셔리 다크 모드 스타일을 적용합니다.

*   **Cyber Charcoal (#0D0E12)**: 80% 이상의 배경 영역에 활용되는 깊은 무중력의 우주 공간감.
*   **Neon Pulse Blue (#00E5FF)**: 핵심 타이틀 텍스트 및 데이터 연결선을 시각적으로 발광시키는 미래지향적 블루.
*   **Guardian Orange (#FF6D00)**: Pydantic v2 방어 가드레일, 'Expected Loss 0%'를 타깃하는 핵심 강조 영역.
*   **Purity White (#FFFFFF)**: 높은 가독성을 요구하는 바디 텍스트 및 로고 영역.

---

## ✍️ 2. 극강의 CTR 썸네일 & 배너 카피 (Headline Copy)

독자의 뇌리에 시각적 자극과 함께 강력한 호기심을 선사하는 레이아웃 배치용 문구 디자인입니다.

### [Option A - 테크 에반젤리스트형]
*   **메인 카피**: "와이파이를 껐는데, 에이전트가 코딩을 한다고?"
*   **서브 카피**: 100% 로컬 샌드박스로 가동되는 무결점 AI 1인 기업
*   **시각 팁**: Blue & White 대비 배치를 통해 질문형 호기심 극대화

### [Option B - 정량적 리스크 타격형]
*   **메인 카피**: "Expected Loss = 0"
*   **서브 카피**: Pydantic v2와 E2E 57개 그린 테스트가 증명하는 무결성
*   **시각 팁**: Guardian Orange 백그라운드 블록으로 에러 차단막 형상화

---

## 📐 3. 레이아웃 & 비주얼 그리드 구도 (Layout Grid)

1.  **배경 구성**: Cyber Charcoal 그라데이션 베이스 위에 미세한 도트(dot) 패턴 혹은 로컬 샌드박스를 연상케 하는 옅은 격자형 와이어프레임 배치.
2.  **포커스 피사체**: 화면 우측 하단에 와이파이 안테나가 차단된 스마트폰 화면(내부에 텔레그램 원터치 이모지 버튼이 선명하게 빛나는 모습)을 3D 그래픽 스타일로 사선 배치.
3.  **가드레일 시각화**: 좌측 상단에서 우측 하단의 스마트폰을 보호하는 듯한 주황색 둥근 투명 배리어(Barrier) 레이어를 합성하여 'Pydantic v2 방어선' 표현.
4.  **카피 배치**: 화면 좌측 중앙에 시각 무게중심을 맞추어 메인 카피를 두껍게 좌측 정렬(Left-align)하여 배치.

---

## 🔠 4. 프리미엄 타이포그래피 (Typography System)

글꼴의 디테일이 시각적 완성도의 90%를 결정합니다.

*   **영문 헤드라인**: `Outfit` (구글 폰트) - 기하학적이면서도 지적인 기품을 자랑하는 산세리프 글꼴.
*   **국문 헤드라인**: `Pretendard Bold` - 화면 가독성(UI)에 최적화된 단단하고 신뢰도 높은 인프라 서체.
*   **서브 텍스트**: `Inter Regular` - 모바일 텔레그램 UI 폰트와 유기적 연속성을 이루는 본문 서체.
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
            guide_content = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(f"{ollama_url}/api/generate",
                               json={"model": model, "prompt": prompt, "stream": False},
                               timeout=240)
            r.raise_for_status()
            guide_content = r.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM 호출 실패: {e}. 모의 비주얼 가이드 모드로 안전하게 폴백합니다.")
        guide_content = f"""# 🎨 [PREMIUM VISUAL GUIDE] 테크 무결성 & 오프라인 AI 1인 기업 (Fallback)

*   **배경색**: Cyber Charcoal (#0D0E12)
*   **강조색**: Neon Pulse Blue (#00E5FF) 및 Safety Orange (#FF6D00)
*   **헤드라인 카피**: "와이파이를 끄고 24시간 가동되는 AI 1인 기업의 실체"
*   **서브 카피**: Pydantic v2와 57개 E2E 그린 테스트 패스가 증명하는 무결성 구조
*   **디자인 레이아웃**: 사선 분할을 사용하여 우측에는 텔레그램 폰 화면, 좌측에는 고대비 텍스트 배치.
"""

    # 3. 저장 및 관리
    if not os.path.exists(GUIDES_DIR):
        os.makedirs(GUIDES_DIR, exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M')
    file_name = f"guide_{timestamp}.md"
    file_path = os.path.join(GUIDES_DIR, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(guide_content)
        
    print("\n" + "="*60)
    print(guide_content)
    print("="*60)
    print(f"\n✅ 비주얼 가이드 디자인 지시서 생성 완료: {file_path}")

if __name__ == "__main__":
    main()
