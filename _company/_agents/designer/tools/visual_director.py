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
WRITER_TOOLS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "writer", "tools"))
SECRETARY_TOOLS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "secretary", "tools"))
ACCOUNT = os.path.join(SECRETARY_TOOLS_DIR, "telegram_setup.json")
NAVER_POSTS_DIR = os.path.join(WRITER_TOOLS_DIR, "naver_posts")
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
        print("⚠️ 최신 네이버 포스팅이 없어 기본 감성 치유 컨셉 기반으로 기획합니다.")
        post_src = """# 괜찮은 척하느라, 오늘 하루도 참 많이 애쓴 당신에게
        우리는 타인의 시선을 의식하느라 삼켜버린 내 감정이 많습니다. 
        섣부른 조언 대신 내 마음에게 다정한 이름을 지어주고 침묵 속에서 가만히 머물러주는 시간이 필요해요."""

    # 2. 프롬프트 구성 (비주얼 디렉터 페르소나 강제)
    prompt = f"""당신은 세계적인 프리미엄 디자인 에이전시의 수석 비주얼 디렉터이자, 아날로그 감성 엽서 예술가입니다.
아래의 심리 치유 에세이를 분석하여, 이에 가장 잘 어울리는 1:1 비율의 럭셔리 감성 치유 엽서(Postcard) 비주얼 디자인 지시서(비주얼 가이드)를 작성하세요.

[에세이 콘텐츠 소스]
{post_src}

[비주얼 가이드 필수 기획 사양]
1. 비주얼 컨셉: 에세이의 테마인 '마음 치유', '침묵의 공감', '안도감' 느낌을 극대화한 아날로그 럭셔리 감성 힐링 톤앤매너 (Warm-Beige & Calming Mist).
2. 색상 팔레트: HSL 또는 Hex 컬러 코드가 명시된 3~4개의 따뜻하고 평온한 큐레이션 배색 제안 (예: Warm Beige HSL 34#98#45, Calming Mist HSL 120#12#80, Dawn Orange HSL 20#85#70 등).
3. 엽서 인쇄용 위로 카피: 
   - 독자의 눈물샘을 따뜻하게 자극하고 깊은 소장 욕구를 일으키는 메인 위로 문구 1가지 (예: "너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다").
   - 엽서 하단에 들어갈 서브 텍스트(예: "당신의 마음을 듣습니다 @young_beom_oh").
4. 레이아웃 & 구도 가이드: 
   - 은은한 새벽녘 그라데이션 및 레이아웃 빌드 가이드.
"""

    try:
        if model == "mock-model":
            guide_content = f"""# 🎨 [PREMIUM POSTCARD VISUAL GUIDE] 마음을 묻다 아날로그 엽서

본 비주얼 가이드는 최신 감성 치유 에세이를 심도 있게 분석하여, 고요하면서도 다정한 위로의 에너지를 1:1 아날로그 감성 엽서로 렌더링하기 위해 설계된 디자인 지시서입니다.

---

## 🌈 1. 큐레이션 색상 팔레트 (Harmonious Healing Palette)

디자인 테마는 **'Warm-Beige Calming Mist'**입니다. HSL 웜톤 배색을 적용합니다.

*   **Warm Beige (#F9F6F0)**: 웜 베이지 HSL 34#98#45.
*   **Calming Mist (#D0D3D4)**: 차분한 소프트 그레이 HSL 120#12#80.
*   **Dawn Orange (#F39C12)**: 새벽녘의 오렌지 HSL 20#85#70.
*   **Soft Charcoal (#2C3E50)**: 본문 차콜 서체 HSL 210#30#20.

---

## ✍️ 2. 엽서 인쇄용 위로 카피 (Headline & Sub Copy)

### [엽서 메인 위로 문구]
*   **메인 카피**: "너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다"
*   **서브 카피**: 당신의 마음을 듣습니다. 오영범 마스터

---

## 📐 3. 레이아웃 & 비주얼 그리드 구도 (Postcard Grid)

1.  **배경 구성**: Warm Beige 그라데이션 위에 Calming Mist 안개 오버레이.
2.  **프레임 데코**: 엽서 가장자리에 얇고 섬세한 둥근 사각형 액자 프레임 라인.
3.  **카피 배치**: 화면 중앙 정렬 및 넉넉한 여백 배치.

---

## 🔠 4. 프리미엄 타이포그래피 (Typography System)

*   **한글 위로 본문**: Pretendard Medium.
*   **시그니처 로고**: NanumMyeongjo Italic.
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
        guide_content = f"""# 🎨 [PREMIUM POSTCARD VISUAL GUIDE] 마음을 묻다 아날로그 엽서 (Fallback)

*   **배경색**: Warm Beige (#F9F6F0)
*   **강조색**: Dawn Orange (#F39C12)
*   **메인 카피**: "오늘 하루만큼은 스스로에게 서툴러도 괜찮다"
*   **서브 카피**: 당신의 아픔을 조용히 듣습니다. 오영범 마스터
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

    # 4. 실물 1:1 감성 엽서 이미지 생성 엔진 연동
    main_title_match = re.search(r"메인 카피\s*[:：=]\s*\"(.*?)\"", guide_content)
    if not main_title_match:
        main_title_match = re.search(r"헤드라인 카피\s*[:：=]\s*\"(.*?)\"", guide_content)
    if not main_title_match:
        main_title_match = re.search(r"메인 카피\s*[:：=]\s*(.*?)$", guide_content, re.MULTILINE)
        
    sub_title_match = re.search(r"서브 카피\s*[:：=]\s*(.*?)$", guide_content, re.MULTILINE)
    
    main_title_str = main_title_match.group(1).strip() if main_title_match else '너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다'
    sub_title_str = sub_title_match.group(1).strip() if sub_title_match else '당신의 마음을 듣습니다. 오영범 마스터'
    
    # Remove quotes from extracted titles to avoid double-escaping
    main_title_str = main_title_str.replace('"', '').replace('“', '').replace('”', '')
    sub_title_str = sub_title_str.replace('"', '').replace('“', '').replace('”', '')
    
    generate_images(timestamp, main_title_str, sub_title_str)

# ------------------- [5. Pillow Procedural Graphics Engine Helpers] ------------------- #

def draw_gradient_background(width, height):
    """지정된 크기에 맞춰 Warm Beige HSL 감성 그라데이션 베이스를 생성합니다."""
    from PIL import Image, ImageDraw
    # Warm Beige (#F9F6F0) to Calming Mist (#EBEBE8)
    base = Image.new("RGBA", (width, height), (249, 246, 240, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        factor = y / float(height)
        r = int(249 * (1 - factor) + 235 * factor)
        g = int(246 * (1 - factor) + 232 * factor)
        b = int(240 * (1 - factor) + 225 * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return base

def draw_ambient_glow(image, cx, cy, radius, color):
    """새벽녘의 아치형 은은한 위로 빛(Ambient Glow)을 오버레이로 그려줍니다."""
    from PIL import Image, ImageDraw, ImageFilter
    width, height = image.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for r in range(radius, 0, -4):
        alpha = int(35 * (1 - r / float(radius)) ** 2)
        if alpha > 0:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius / 6))
    return Image.alpha_composite(image, overlay)

def draw_postcard_frame(image):
    """엽서 가장자리에 얇고 섬세한 둥근 사각형 액자 프레임 라인을 그려줍니다."""
    from PIL import ImageDraw
    width, height = image.size
    draw = ImageDraw.Draw(image)
    padding = 45
    line_color = (139, 128, 115, 60) # 차분한 브론즈 톤의 아주 옅은 보더
    draw.rectangle([padding, padding, width - padding, height - padding], outline=line_color, width=1)
    return image

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

def draw_centered_postcard_text(image, main_lines, sub_lines):
    """메인 카피와 서브 카피를 가로/세로 비율을 고려하여 중앙 정렬로 미려하게 배치합니다."""
    from PIL import ImageDraw
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    font_main = get_premium_font(34, is_bold=True)
    font_sub = get_premium_font(20, is_bold=False)
    font_sig = get_premium_font(15, is_bold=True)
    
    text_color = (60, 50, 40, 255) # 부드러운 다크 차콜 브라운
    sub_color = (110, 95, 80, 255)  # 웜 그레이 브라운
    
    # 1. 엽서 최상단 브랜드 로고 배치
    sig_text = "마음을 묻다  |  오영범 마스터"
    try:
        sig_w = font_sig.getlength(sig_text)
    except Exception:
        sig_w = len(sig_text) * 10
    draw.text(((width - sig_w) // 2, 130), sig_text, font=font_sig, fill=sub_color)
    
    # 로고 밑 얇은 골드 데코레이션 라인
    line_w = 80
    draw.line([((width - line_w) // 2, 175), ((width + line_w) // 2, 175)], fill=(139, 128, 115, 50), width=1)
    
    # 2. 메인 & 서브 카피 세로 중심 정렬 연산
    main_spacing = 22
    sub_spacing = 15
    
    main_line_height = (font_main.size if font_main else 34) + main_spacing
    sub_line_height = (font_sub.size if font_sub else 20) + sub_spacing
    
    total_content_h = (len(main_lines) * main_line_height) + 70 + (len(sub_lines) * sub_line_height)
    start_y = 230 + (550 - total_content_h) // 2
    
    # 3. 메인 위로 문구 렌더링
    y = start_y
    for line in main_lines:
        try:
            line_w = font_main.getlength(line)
        except Exception:
            line_w = len(line) * 20
        # 소프트 섀도우 추가로 프리미엄 감성 주입
        draw.text(((width - line_w) // 2 + 1, y + 1), line, font=font_main, fill=(139, 128, 115, 30))
        draw.text(((width - line_w) // 2, y), line, font=font_main, fill=text_color)
        y += main_line_height
        
    y += 45 # 문단 간격
    
    # 4. 서브 본문/발신처 렌더링
    for line in sub_lines:
        try:
            line_w = font_sub.getlength(line)
        except Exception:
            line_w = len(line) * 11
        draw.text(((width - line_w) // 2, y), line, font=font_sub, fill=sub_color)
        y += sub_line_height

def generate_images(timestamp, main_title=None, sub_title=None):
    """'마음을 묻다' 특화 1:1 감성 치유 엽서(1000x1000px) 실물 PNG 파일을 생성합니다."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("⚠️ Pillow 라이브러리가 설치되지 않아 이미지 그리기를 건너뜜.")
        return
        
    print("🎨 [Pillow Graphics Engine] Generating Premium Healing Postcard...")
    
    if not main_title:
        main_title = "너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다"
    if not sub_title:
        sub_title = "당신의 마음을 듣습니다. 오영범 마스터"

    # 1. 1000x1000 1:1 캔버스 그라데이션 및 레이아웃 빌드
    img_postcard = draw_gradient_background(1000, 1000)
    
    # 새벽녘 오렌지빛의 포근한 위로 원광 (Dawn Orange)
    img_postcard = draw_ambient_glow(img_postcard, 500, 500, 480, (243, 156, 18))
    # 소프트 프레임 라인 드로잉
    img_postcard = draw_postcard_frame(img_postcard)
    
    font_main = get_premium_font(34, is_bold=True)
    font_sub = get_premium_font(20, is_bold=False)
    
    # 텍스트 줄바꿈 계산 (여백을 위해 넉넉한 너비 제약)
    lines_main = wrap_text(main_title, font_main, 760)
    lines_sub = wrap_text(sub_title, font_sub, 800)
    
    # 중앙 정렬 텍스트 합성
    draw_centered_postcard_text(img_postcard, lines_main, lines_sub)
    
    # 2. 저장 처리
    postcard_name = f"postcard_{timestamp}.png"
    postcard_path = os.path.join(GUIDES_DIR, postcard_name)
    
    img_postcard.save(postcard_path, "PNG")
    print(f"✅ Real Premium Healing Postcard Generated: {postcard_path}")
    
    # 3. 텔레그램으로 즉시 자동 발송 시도
    _api_send_photos_to_telegram(postcard_path, main_title)

def _api_send_photos_to_telegram(postcard_path, caption_text):
    """비서 설정을 읽어와 새로 생성된 실물 치유 엽서 이미지를 사장님 텔레그램 채널로 즉시 전송합니다."""
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
        
        with open(postcard_path, "rb") as f_photo:
            files = {"photo": f_photo}
            data = {
                "chat_id": chat_id,
                "caption": f"✉️ [마음을 묻다 — 실물 엽서 출고]\n\n\"{caption_text}\"\n\n오영범 마스터가 마음을 담아 빚어낸 1:1 감성 치유 엽서 실물입니다."
            }
            requests.post(url, data=data, files=files, timeout=20)
            
        print("🚀 [Telegram Pushing] Successfully sent 1:1 healing postcard directly to your Telegram chat!")
    except Exception as e:
        print(f"⚠️ 텔레그램 이미지 발송 중 에러: {e}")

if __name__ == "__main__":
    main()
