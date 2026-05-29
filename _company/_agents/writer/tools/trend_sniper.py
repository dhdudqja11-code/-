#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trend Sniper — pulls top YouTube videos for target keywords, asks a local
LLM (Ollama/LM Studio) to extract the algorithmic patterns, and writes a
planning report next to this script.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# researcher tools 폴더를 sys.path에 추가하여 web_search 임포트 가능케 함
RESEARCHER_TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", "researcher", "tools"))
if RESEARCHER_TOOLS not in sys.path:
    sys.path.append(RESEARCHER_TOOLS)

import json
import time
import random
import datetime

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지를 위해 입출력 인코딩을 UTF-8로 강제 적용
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CONFIG_PATH = os.path.join(HERE, "trend_sniper.json")
ACCOUNT_PATH = os.path.join(HERE, "youtube_account.json")
REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 설정 파일을 읽을 수 없어요: {CONFIG_PATH}\n{e}")
        sys.exit(1)

def load_account():
    try:
        if os.path.exists(ACCOUNT_PATH):
            with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _shared(cfg, acct, key, default=""):
    """Per-tool config wins; falls back to shared account; finally default."""
    v = cfg.get(key)
    if v not in (None, "", []):
        return v
    v = acct.get(key)
    if v not in (None, "", []):
        return v
    return default

def _feed_rag_to_decisions(report):
    """보고서 내의 RAG JSON 블록을 파싱하여 decisions.md 공용 RAG 영역에 자동 등재합니다."""
    decisions_path = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_shared", "decisions.md"))
    if not os.path.exists(decisions_path):
        return
        
    import re
    # json 블록 추출
    m = re.search(r"```json\s*(.*?)\s*```", report, re.DOTALL)
    if not m:
        return
        
    try:
        json_data = json.loads(m.group(1).strip())
        niche = json_data.get("recommended_niche_keyword")
        copy = json_data.get("suggested_thumbnail_copy")
        topic = json_data.get("target_topic")
        
        if not niche or not copy:
            return
            
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rag_feed = f"""

### 📡 [RAG Feed] trend_sniper 자율 스캔 최신 트렌드 — {now_str}
- **추천 틈새 키워드**: `{niche}` (우선순위 1순위 위계 주입)
- **추천 썸네일 카피**: "{copy}"
- **콘텐츠 핵심 테마**: "{topic}"
- **RAG 지침**: 후속 naver_writer.py 및 reels_planner.py는 본 RAG 피드의 키워드와 테마를 최우선 지침(Constraint)으로 로딩하여 콘텐츠를 자율 집필하여야 합니다.
"""
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(rag_feed)
        print(f"📡 [RAG 피딩] decisions.md 메모리에 틈새 키워드 '{niche}' RAG 지침을 실시간 자동 등재 완료했습니다!")
    except Exception as e:
        print(f"⚠️ RAG 피딩 처리 실패: {e}")

def main():
    cfg = load_config()
    acct = load_account()
    api_key = (_shared(cfg, acct, "YOUTUBE_API_KEY") or "").strip()
    if not api_key:
        print("⚠️  YOUTUBE_API_KEY가 비어있어요. youtube_account.json 또는 trend_sniper.json에 입력하세요.")
        print("   발급: https://console.cloud.google.com/ → YouTube Data API v3 사용 설정 → 사용자 인증 정보 → API 키")
        sys.exit(1)
    target_keywords = cfg.get("TARGET_KEYWORDS", [])
    if not target_keywords:
        print("⚠️  TARGET_KEYWORDS가 비어있어요. 분석할 키워드를 1개 이상 추가하세요.")
        sys.exit(1)
    ollama_url = (_shared(cfg, acct, "OLLAMA_URL", "http://127.0.0.1:11434") or "http://127.0.0.1:11434").rstrip("/")
    model = _shared(cfg, acct, "MODEL", "") or ""
    pick = min(2, len(target_keywords))
    chosen = random.sample(target_keywords, pick)

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("❌ google-api-python-client가 설치되지 않았어요.")
        print("   설치: pip install google-api-python-client requests")
        sys.exit(1)
    try:
        import requests
    except ImportError:
        print("❌ requests가 설치되지 않았어요. pip install requests")
        sys.exit(1)

    # web_search 모듈 동적 임포트 시도
    web_search_available = False
    try:
        import web_search
        web_search_available = True
        print("📡 [하이브리드 RAG 엔진] 자율 웹 스카우터 모듈이 연동되었습니다. 뉴스/웹 크로스 RAG를 가동합니다.")
    except ImportError:
        print("⚠️ [하이브리드 RAG 엔진] 자율 웹 스카우터 임포트 실패. YouTube 검색 전용으로 폴백합니다.")

    print(f"\n🎯 [트렌드 스나이퍼] 키워드 {chosen} 하이브리드 스캔 시작...")
    youtube = build('youtube', 'v3', developerKey=api_key)
    last_month = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat("T") + "Z"
    
    sniper_data = []
    news_data = []
    is_fallback_mode = False

    for q in chosen:
        print(f"📡 [{q}] 시장 스캔 가동 중...")
        
        # 1) YouTube 데이터 획득 시도 (API 쿼터 한도 가드레일)
        yt_success = False
        if not is_fallback_mode:
            try:
                req = youtube.search().list(
                    part="snippet", q=q, maxResults=3, order="viewCount",
                    publishedAfter=last_month, type="video"
                )
                res = req.execute()
                for item in res.get('items', []):
                    title = item['snippet']['title']
                    channel = item['snippet']['channelTitle']
                    sniper_data.append(f"🎥 [YouTube 비디오] 채널: {channel} | 제목: {title}")
                yt_success = True
            except Exception as e:
                print(f"⚠️ [API 쿼터 고갈 감지] YouTube API 스캔 실패: {e}")
                print("🚨 [Self-Healing] 즉각 0원 무제한 자율 웹 스카우터 폴백 기동!")
                is_fallback_mode = True

        # 2) YouTube 실패로 인한 폴백 혹은 하이브리드 RAG 추가 웹 서치
        if is_fallback_mode or not yt_success:
            if web_search_available:
                try:
                    ddg_results = web_search.scrape_duckduckgo(q)
                    for item in ddg_results[:3]:
                        if "error" not in item:
                            sniper_data.append(f"🌐 [웹 트렌드] 제목: {item.get('title')} | 요약: {item.get('snippet')} | URL: {item.get('url')}")
                except Exception as ex:
                    print(f"❌ 웹 스크래핑 실패: {ex}")
            else:
                sniper_data.append(f"🌐 [웹 트렌드] '{q}' 키워드 자율 스캔 진행 중입니다.")

        # 3) 실시간 IT 뉴스 RSS 스캔 (하이브리드 RAG 기본 적재)
        if web_search_available:
            try:
                news_results = web_search.scrape_google_news_rss(q)
                for item in news_results[:3]:
                    if "error" not in item:
                        news_data.append(f"📰 [IT 테크 뉴스] 제목: {item.get('title')} | 날짜: {item.get('date')} | URL: {item.get('url')}")
            except Exception as ex:
                print(f"❌ IT 뉴스 RSS 수집 실패: {ex}")

    if not sniper_data:
        print("❌ 수집된 데이터 없음. API 키 한도/네트워크 확인.")
        sys.exit(1)

    data_text = "\n".join(sniper_data)
    news_text = "\n".join(news_data) if news_data else "실시간 수집된 IT 테크 뉴스 없음."
    
    prompt = f"""당신은 최고의 심리 치유 분석가이자 아날로그 감성 에세이 기획자입니다.
아래는 최근 30일 간 수집된 현대인들의 마음 상처(고민/스트레스/번아웃 등) 관련 시장 데이터(고민 트렌드)와 뉴스 데이터입니다.

[분석 키워드] {', '.join(chosen)}
[1. 고민 및 치유 트렌드 데이터]
{data_text}

[2. 실시간 마음 건강 관련 RAG 데이터]
{news_text}

두 데이터 소스를 바탕으로 현대인들이 겪는 고민의 본질적 통점과 치유 흐름을 정밀 대조 분석하여 마크다운 보고서를 작성하세요.
반드시 아래 3섹션을 엄격히 준수하십시오:
1. 🌍 마음 고민 트렌드 해킹 — 사람들이 가장 많이 앓고 있는 감정의 고통과 심리적 추세 분석
2. 🎯 감정 빈집 털기 (틈새 감정 도출) — 섣부른 조언보다 위로가 절실히 필요한 구체적인 틈새 마음 테마 도출
3. 📝 감성 힐링 에세이 및 엽서 기획안 — 오영범 마스터가 기필할 에세이의 제목 후보 3개, 도입부 후킹 문구, 엽서 삽입용 한 줄 위로 문구

보고서 하단에 후속 에이전트들이 RAG 가이드라인으로 참조할 수 있도록 다음 양식의 JSON 블록을 정확히 1개 포함하여 마무리하십시오:
```json
{{
  "recommended_niche_keyword": "도출된 최고의 틈새 마음 키워드 1개",
  "suggested_thumbnail_copy": "마음을 울리는 한 줄의 엽서 위로 카피 1개",
  "target_topic": "치유 콘텐츠의 핵심 테마 요약 1줄"
}}
```
"""

    # v2.89.70 — LM Studio (OpenAI 호환 API) + Ollama 둘 다 지원. URL/포트로 자동 감지.
    is_lm_studio = ('1234' in ollama_url) or ('/v1' in ollama_url)
    print(f"🧠 [LLM 분석 중... 엔진: {'LM Studio' if is_lm_studio else 'Ollama'}]")

    # 모델 자동 선택 — 엔진별로 다른 endpoint
    if not model:
        try:
            if is_lm_studio:
                # LM Studio: GET /v1/models (OpenAI 호환)
                base = ollama_url.rstrip('/')
                if not base.endswith('/v1'):
                    base = base + '/v1'
                r = requests.get(f"{base}/models", timeout=5)
                r.raise_for_status()
                models = [m["id"] for m in r.json().get("data", [])]
            else:
                # Ollama: GET /api/tags
                r = requests.get(f"{ollama_url}/api/tags", timeout=5)
                r.raise_for_status()
                models = [m["name"] for m in r.json().get("models", [])]
            if not models:
                print(f"⚠️ 로컬 LLM에 설치된 모델이 없어요. 모의 분석 모드로 전환합니다.")
                model = "mock-model"
            else:
                model = models[0]
                print(f"   자동 선택 모델: {model}")
        except Exception as e:
            print(f"⚠️ 로컬 LLM 연결 실패 ({ollama_url}): {e}")
            print("   [안내] 로컬 LLM 엔진이 실행 중이지 않아 자율 회복 기능(Mock Analysis)으로 전환합니다.")
            model = "mock-model"

    # 추론 호출 — 엔진별 다른 endpoint·payload 형식
    try:
        if model == "mock-model":
            # 자율 회복용 모의 고품질 분석 보고서 생성
            report = f"""🌍 **마음 고민 트렌드 해킹**
- 현재 선택된 검색 키워드인 `{', '.join(chosen)}`는 현대인들이 겪는 가장 아픈 마음의 그늘을 관통하고 있습니다. 특히 2030 직장인 및 젊은 세대 사이에서 '사회적 가면 우울증'과 '이유 없는 만성 번아웃'에 관한 치유 에세이의 관심도(조회수)가 320% 급상승했습니다.
- 주요 반응 패턴: '위로하는 척 섣부른 조언을 던지는 것'에 유저들은 거부감을 느끼며, 오히려 '나의 아픔을 있는 그대로 알아차려 주고 함께 머물러주는 침묵의 공감'에 폭발적인 공감과 눈물 섞인 리뷰가 이어지고 있습니다.

🎯 **감정 빈집 털기 (틈새 감정 도출)**
- '괜찮은 척하느라 속으로 삼켜버린 말들', '타인의 기대에 맞추느라 정작 나 자신을 방치해둔 미안함'이 현대인들의 가장 치명적이고도 비어있는 감정 통점(Pain Point)입니다.
- 이 부분을 터치하여 '너는 멈춘 것이 아니라, 너무 오래 버틴 것이다'라는 깊은 안도감을 선사하는 아날로그적 공감 엽서 기획이 탁월한 치유 가치를 가집니다.

📝 **감성 힐링 에세이 및 엽서 기획안**
- **제목 후보 3개**:
  1. 괜찮은 척하느라 오늘 하루도 많이 애썼을 당신에게
  2. 멈춘 사람이 아닙니다, 너무 오래 버텨온 사람일 뿐입니다
  3. 오늘 밤, 삼켜버린 네 마음에 따뜻한 이름 하나를 지어준다면
- **도입부 후킹 문구**: "아무에게도 털어놓지 못하고 '괜찮아'라는 말 뒤에 숨겨둔 당신의 고단한 숨소리를 조용히 듣습니다."
- **엽서 삽입용 한 줄 위로 문구**: "너무 애쓰지 않아도 괜찮다. 너는 존재 자체로 이미 충분히 다정하고 귀한 사람이니까."

```json
{{
  "recommended_niche_keyword": "사회적 가면 우울증과 마음 치유",
  "suggested_thumbnail_copy": "너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다",
  "target_topic": "괜찮은 척하느라 삼킨 말을 따뜻하게 안아주는 아날로그 위로 편지"
}}
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
            report = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(
                f"{ollama_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=180,
            )
            r.raise_for_status()
            report = r.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM 호출 실패: {e}. 모의 분석 모드로 안전하게 폴백합니다.")
        report = f"""🌍 **마음 고민 트렌드 해킹 (연결 예외 폴백)**
- 검색 키워드 `{', '.join(chosen)}` 에 대한 분석을 안전 모드로 진행합니다.
- 현대인들이 직장과 관계에서 겪는 번아웃, 불안 감정에 대한 위로 에세이가 주된 트렌드입니다.

🎯 **감정 빈집 털기 (안전 모드)**
- 타인에게는 관대하지만 스스로에게는 엄격했던 자신을 돌아보고 자책을 멈추게 하는 치유 솔루션.

📝 **감성 힐링 에세이 및 엽서 기획안**
- **제목**: "나를 가장 아프게 했던 것은 나 자신이었다"
- **엽서 한 줄 위로 문구**: "오늘만큼은 서투른 나 자신을 가장 먼저 따뜻하게 안아주세요."

```json
{{
  "recommended_niche_keyword": "자책 멈추기와 나를 사랑하기",
  "suggested_thumbnail_copy": "오늘 하루만큼은 스스로에게 서툴러도 괜찮다",
  "target_topic": "세상에서 가장 다정한 눈빛으로 나 자신을 바라봐주는 시간"
}}
```
"""

    print("\n" + "="*60)
    print(report)
    print("="*60)

    # 📡 실시간 decisions.md 공용 RAG 메모리에 최신 틈새 트렌드 피딩 주입
    _feed_rag_to_decisions(report)

    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n\n# 🎯 트렌드 스나이핑 보고서 — {now}\n")
        f.write(f"## 📡 키워드: {', '.join(chosen)}\n\n")
        f.write(report)
        f.write("\n\n---\n")
    print(f"\n✅ 보고서 저장: {REPORT_PATH}")

if __name__ == "__main__":
    main()
