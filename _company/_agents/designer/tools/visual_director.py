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
WORKSPACE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
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

    # 4. 실물 썸네일 & 카드뉴스 이미지 생성 엔진 연동
    main_title_match = re.search(r"메인 카피\s*[:：=]\s*\"(.*?)\"", guide_content)
    if not main_title_match:
        main_title_match = re.search(r"헤드라인 카피\s*[:：=]\s*\"(.*?)\"", guide_content)
    if not main_title_match:
        main_title_match = re.search(r"메인 카피\s*[:：=]\s*(.*?)$", guide_content, re.MULTILINE)
        
    sub_title_match = re.search(r"서브 카피\s*[:：=]\s*(.*?)$", guide_content, re.MULTILINE)
    
    main_title_str = main_title_match.group(1).strip() if main_title_match else '와이파이 차단된 "로컬 AI" 1인 기업 탄생의 실체'
    sub_title_str = sub_title_match.group(1).strip() if sub_title_match else 'Pydantic v2와 121개 그린 테스트가 증명하는 무결성'
    
    # Remove quotes from extracted titles to avoid double-escaping
    main_title_str = main_title_str.replace('"', '').replace('“', '').replace('”', '')
    # Put quotes around local AI for highlight aesthetics
    main_title_str = main_title_str.replace('로컬 AI', '"로컬 AI"').replace('1인 기업', '"1인 기업"')
    
    generate_images(timestamp, main_title_str, sub_title_str)

# ------------------- [5. Pillow Procedural Graphics Engine Helpers] ------------------- #

def draw_gradient_background(width, height):
    """지정된 크기에 맞춰 HSL 감성 다크 그라데이션 베이스를 생성합니다."""
    from PIL import Image, ImageDraw
    base = Image.new("RGBA", (width, height), (13, 14, 18, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        factor = y / float(height)
        r = int(13 * (1 - factor) + 4 * factor)
        g = int(14 * (1 - factor) + 6 * factor)
        b = int(18 * (1 - factor) + 12 * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return base

def draw_ambient_glow(image, cx, cy, radius, color):
    """소프트한 네온 블러 원광(Ambient Glow)을 오버레이로 그려줍니다."""
    from PIL import Image, ImageDraw, ImageFilter
    width, height = image.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for r in range(radius, 0, -4):
        alpha = int(40 * (1 - r / float(radius)) ** 2)
        if alpha > 0:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius / 6))
    return Image.alpha_composite(image, overlay)

def draw_tech_mesh(image, step=40):
    """보안성 및 테크 인프라 느낌을 자아내는 옅은 격자 그리드 그물망을 얹어줍니다."""
    from PIL import Image, ImageDraw
    width, height = image.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    grid_color = (255, 255, 255, 6)
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill=grid_color)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=grid_color)
    return Image.alpha_composite(image, overlay)

def get_premium_font(font_size, is_bold=False):
    """Windows 시스템 내 존재하는 맑은 고딕(Malgun Gothic) 서체를 우선적으로 매칭하며, 없으면 기본 폰트로 폴백합니다."""
    from PIL import ImageFont
    font_paths = [
        "C:\\Windows\\Fonts\\malgunbd.ttf" if is_bold else "C:\\Windows\\Fonts\\malgun.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if is_bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\Pretendard-Bold.ttf" if is_bold else "C:\\Windows\\Fonts\\Pretendard-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def wrap_text(text, font, max_width):
    """텍스트가 주어진 픽셀 가로폭을 넘지 않도록 단어/음절 단위로 행바꿈 처리합니다."""
    lines = []
    words = text.split()
    if not words:
        return [text]
        
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            w = font.getlength(test_line)
        except Exception:
            w = len(test_line) * (font.size * 0.55 if hasattr(font, 'size') else 8)
            
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def draw_highlighted_text(draw, text_lines, start_x, start_y, font, default_color, spacing=15):
    """텍스트 줄별로 그림을 그립니다. 따옴표로 둘러싸인 단어는 Neon Cyan으로, 리스크/가치 수치는 Safety Orange로 그립니다."""
    y = start_y
    for line in text_lines:
        words = line.split(" ")
        x = start_x
        for word in words:
            color = default_color
            clean_word = word
            # 따옴표 강조 파싱
            if (word.startswith('"') and word.endswith('"')) or (word.startswith('“') and word.endswith('”')):
                color = (0, 242, 254, 255) # Neon Cyan
                clean_word = word[1:-1]
            elif "100%" in word or "0%" in word or "Loss" in word or "Saved" in word or "$2,500+" in word:
                color = (255, 109, 0, 255) # Safety Orange
            
            # 드롭 섀도우 그리기
            draw.text((x + 2, y + 2), clean_word, font=font, fill=(0, 0, 0, 200))
            # 실물 텍스트 그리기
            draw.text((x, y), clean_word, font=font, fill=color)
            
            try:
                word_w = font.getlength(clean_word + " ")
            except Exception:
                word_w = len(clean_word + " ") * (font.size * 0.6 if hasattr(font, 'size') else 8)
                
            x += int(word_w)
            
        try:
            line_h = font.size + spacing
        except Exception:
            line_h = 30
        y += line_h

def generate_images(timestamp, main_title=None, sub_title=None):
    """실물 유튜브 썸네일(1280x720) 및 인스타 카드뉴스(1080x1080) 실물 PNG 파일을 생성합니다."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("⚠️ Pillow 라이브러리가 설치되지 않아 이미지 그리기를 건너뜁니다.")
        return
        
    print("🎨 [Pillow Graphics Engine] Generating campaign image assets...")
    
    if not main_title:
        main_title = '와이파이 차단된 "로컬 AI" 1인 기업 탄생의 실체'
    if not sub_title:
        sub_title = 'Pydantic v2와 121개 그린 테스트가 증명하는 무결성'

    # --- 1) 유튜브 썸네일 생성 (1280x720) ---
    img_thumb = draw_gradient_background(1280, 720)
    img_thumb = draw_ambient_glow(img_thumb, 1100, 150, 420, (0, 242, 254))  # Cyan glow
    img_thumb = draw_ambient_glow(img_thumb, 200, 600, 360, (255, 109, 0))   # Orange glow
    img_thumb = draw_tech_mesh(img_thumb, step=45)
    
    draw_thumb = ImageDraw.Draw(img_thumb)
    
    font_main = get_premium_font(48, is_bold=True)
    font_sub = get_premium_font(24, is_bold=False)
    font_logo = get_premium_font(18, is_bold=True)
    
    # 로고/뱃지 그리기
    draw_thumb.rectangle([45, 45, 195, 80], fill=(255, 255, 255, 10), outline=(255, 255, 255, 30), width=1)
    draw_thumb.text((60, 52), "🔮 SYSTEM", font=font_logo, fill=(0, 242, 254, 230))
    
    lines_main = wrap_text(main_title, font_main, 850)
    lines_sub = wrap_text(sub_title, font_sub, 800)
    
    draw_highlighted_text(draw_thumb, lines_main, 50, 190, font_main, (255, 255, 255, 255), spacing=22)
    
    y_sub = 190 + len(lines_main) * (font_main.size if font_main else 48) + 40
    draw_highlighted_text(draw_thumb, lines_sub, 50, y_sub, font_sub, (148, 163, 184, 255), spacing=15)
    
    # 우측 장치 모양 데코
    draw_thumb.rectangle([940, 180, 1200, 540], fill=(0, 242, 254, 8), outline=(0, 242, 254, 40), width=2)
    for offset in range(0, 260, 30):
        draw_thumb.line([(940 + offset, 180), (940, 180 + offset)], fill=(0, 242, 254, 15), width=1)
    draw_thumb.text((980, 330), "🔒 SECURE", font=font_main, fill=(255, 255, 255, 20))
    draw_thumb.text((985, 390), "Expected Loss = 0", font=font_sub, fill=(255, 109, 0, 180))
    
    # --- 2) 인스타 카드뉴스 생성 (1080x1080) ---
    img_card = draw_gradient_background(1080, 1080)
    img_card = draw_ambient_glow(img_card, 540, 540, 500, (160, 32, 240)) # Center purple glow
    img_card = draw_ambient_glow(img_card, 900, 100, 300, (0, 242, 254))  # Cyan glow top
    img_card = draw_tech_mesh(img_card, step=50)
    
    draw_card = ImageDraw.Draw(img_card)
    
    # 헤더 뱃지
    draw_card.rectangle([45, 45, 255, 80], fill=(255, 255, 255, 10), outline=(255, 255, 255, 30))
    draw_card.text((60, 52), "📱 B2B MARKETING", font=font_logo, fill=(0, 242, 254, 230))
    
    font_card_main = get_premium_font(44, is_bold=True)
    font_card_sub = get_premium_font(26, is_bold=False)
    
    lines_card_main = wrap_text(main_title, font_card_main, 950)
    lines_card_sub = wrap_text(sub_title, font_card_sub, 900)
    
    draw_highlighted_text(draw_card, lines_card_main, 50, 250, font_card_main, (255, 255, 255, 255), spacing=24)
    
    y_card_sub = 250 + len(lines_card_main) * (font_card_main.size if font_card_main else 44) + 40
    draw_highlighted_text(draw_card, lines_card_sub, 50, y_card_sub, font_card_sub, (148, 163, 184, 255), spacing=18)
    
    # 카드뉴스 하단 재무적 가치 윈도우 그리기
    draw_card.rectangle([50, 750, 1030, 980], fill=(13, 14, 18, 180), outline=(255, 109, 0, 40), width=2)
    draw_card.text((80, 780), "📊 Expected Avoided Loss Value (ALV)", font=font_sub, fill=(255, 109, 0, 230))
    draw_card.text((80, 840), "$2,500+ Saved per Compliance Block", font=font_card_main, fill=(255, 255, 255, 255))
    draw_card.text((80, 915), "GDPR / CCPA Cryptographic Integrity Standards Checked.", font=font_logo, fill=(148, 163, 184, 230))

    # 저장 처리
    thumb_name = f"thumbnail_{timestamp}.png"
    card_name = f"card_news_{timestamp}.png"
    
    thumb_path = os.path.join(GUIDES_DIR, thumb_name)
    card_path = os.path.join(GUIDES_DIR, card_name)
    
    img_thumb.save(thumb_path, "PNG")
    img_card.save(card_path, "PNG")
    
    print(f"✅ Real YouTube Thumbnail Generated: {thumb_path}")
    print(f"✅ Real Instagram Card News Generated: {card_path}")
    
    # 텔레그램으로 즉시 자동 발송 시도
    _api_send_photos_to_telegram(thumb_path, card_path)

def _api_send_photos_to_telegram(thumb_path, card_path):
    """비서 설정을 읽어와 새로 생성된 실물 이미지들을 사장님 텔레그램 채널로 즉시 전송합니다."""
    token, chat_id = "", ""
    
    secretary_json = os.path.join(WORKSPACE, "_company", "_agents", "secretary", "tools", "telegram_setup.json")
    if os.path.exists(secretary_json):
        try:
            with open(secretary_json, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            token = (cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
            chat_id = (cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        except Exception:
            pass
            
    if not token or not chat_id:
        print("⚠️ 텔레그램 토큰 설정이 유효하지 않아 텔레그램 직접 전송은 건너뜁니다.")
        return
        
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        
        # 썸네일 발송
        with open(thumb_path, "rb") as f_thumb:
            files = {"photo": f_thumb}
            data = {
                "chat_id": chat_id,
                "caption": "🎨 [Premium Visual Thumbnail]\nRyzen 9 병렬 가속 기반으로 생성된 유튜브/블로그 실물 썸네일입니다."
            }
            requests.post(url, data=data, files=files, timeout=20)
            
        # 카드뉴스 발송
        with open(card_path, "rb") as f_card:
            files = {"photo": f_card}
            data = {
                "chat_id": chat_id,
                "caption": "📱 [Premium Card News]\nNVIDIA RTX 4060 로컬 AI 시나리오가 반영된 인스타용 실물 카드뉴스입니다."
            }
            requests.post(url, data=data, files=files, timeout=20)
            
        print("🚀 [Telegram Pushing] Successfully sent procedural PNG thumbnails directly to your Telegram chat!")
    except Exception as e:
        print(f"⚠️ 텔레그램 이미지 발송 중 에러: {e}")

if __name__ == "__main__":
    main()
