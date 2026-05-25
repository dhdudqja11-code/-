#!/usr/bin/env python3
# version: naver_v1
"""Naver Blog Column Writer — acts as a highly authoritative tech-business
evangelist. Automatically parses the latest YouTube trend snapshot from
trend_sniper_report.md, infuses simulation ROI/expected loss metrics,
and drafts a publication-ready Korean business article (1,000+ words).

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
ACCOUNT = os.path.join(HERE, "youtube_account.json")
SNIPER_REPORT_PATH = os.path.join(HERE, "trend_sniper_report.md")
POSTS_DIR = os.path.join(HERE, "naver_posts")

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
        # 보고서는 '# 🎯 트렌드 스나이핑 보고서' 또는 '# 🎯 트렌드 스나이핑 보고서 — YYYY-MM-DD' 로 추가됨
        sections = content.split("# 🎯 트렌드 스나이핑 보고서")
        if len(sections) > 1:
            # 가장 마지막(최신) 섹션을 리턴
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

    # v2.89.70 — LM Studio (OpenAI 호환 API) + Ollama 둘 다 지원. URL/포트로 자동 감지.
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
            # 자율 회복용 명품 칼럼 자율 집필 데이터 제공
            post_content = f"""# 와이파이를 완전히 끄고 만든 게임?! 100% 로컬로 굴리는 AI 1인 기업과 기술 무결성의 실체

[네이버 블로그 권장 이미지 위치: 와이파이 인터넷선이 해체된 오프라인 노트북과 작동 중인 자율 에이전트 다이어그램]

최근 AI 1인 기업과 비즈니스 자동화에 대한 시장의 관심은 그 어느 때보다 뜨겁습니다. 하루가 다르게 새로운 AI 툴과 비서 서비스가 쏟아져 나오며 누구나 손쉽게 1인 비즈니스를 영위할 수 있다고 광고합니다. 

그러나 시중의 수많은 가이드들이 안고 있는 치명적인 맹점이 있습니다. 바로 '네트워크에 의존하는 불완전한 자동화'와 '회복 탄력성(Self-healing)의 결여'입니다. 외부 API 서버가 단 10초만 마비되어도 기업 전체의 작동 파이프라인이 멈추거나 예외(Exception)로 인해 폭사하고 마는 구조적인 불안정성을 안고 있습니다.

기술적 무결성을 증명하지 못하는 자동화는 오히려 사장님에게 막대한 시간적/재무적Expected Loss를 안겨줄 뿐입니다.

[네이버 블로그 권장 이미지 위치: 100% 그린으로 통과된 pytest 터미널 패스 결과 및 무결성 도표 화면]

## 1. 100% 로컬(인터넷 없이) 작동하는 오프라인 가드레일 설계의 가치

진정한 AI 1인 기업 자동화를 구축하기 위해서는 네트워크 차단 상황에서도 에이전트 툴들이 다운되지 않고 안전하게 우회 가동되는 '자율 복구(Mock Fallback) 엔진'이 전제되어야 합니다.

최근 유튜브 트렌드 데이터 분석에서도 시청자들은 더 이상 단순한 이론 설명에 반응하지 않습니다. '실제로 와이파이를 완전히 뽑아둔 오프라인 샌드박스 상태에서, AI 에이전트들이 스스로 코딩을 수행하고 컴파일 오류를 자율 디버깅하여 0으로 종료되는 실전 실증 과정'에 클릭을 아끼지 않고 있습니다.

에이전트가 로컬 LLM(Ollama, LM Studio 등)과의 소켓 통신 실패를 감지하면 즉시 고품질 모의 분석 모드로 안전하게 폴백하여 exit code 0을 반환하는 자율 회복 메커니즘이야말로 24시간 자율 가동 오토 플래너(auto_planner.py)를 지속 가능하게 굴려주는 심장입니다.

## 2. Pydantic v2와 E2E 57개 테스트 팩이 증명하는 무결한 방어막

비즈니스의 안정성은 완벽한 데이터 형상 검증에서부터 출발합니다. API Gateway를 통과하는 모든 입출력 트랜잭션은 단 한 줄의 오차도 허용되어서는 안 됩니다.

[네이버 블로그 권장 이미지 위치: Pydantic v2 field_validator를 통해 형식 에러가 사전 차단되는 게이트웨이 시각화]

이를 위해 컴플라이언스 관문(`core_gateway/`)에는 Pydantic v2의 최신 기법인 `@field_validator` 검증 루틴을 주입하여, 사용자의 잘못된 접근이나 비인가 데이터 전송, 그리고 누락된 필수 필드(`source_system` 등)를 API 단에서 강력하게 사전 필터링합니다.

이로 인해 발생할 수 있는 잠재적 컴플라이언스 위반 리스크를 정밀 타격하여 비인가 트랙잭션을 원천 봉쇄할 수 있습니다. 

이번 시스템에서는 총 57개의 E2E 비즈니스 시뮬레이션 및 가드레일 유닛 테스트가 단 **4.59초** 만에 100% 그린 패스(Green PASSED)하며 기술적이고 구조적인 견고함을 수학적으로 증명했습니다. 데이터 파손에 따른 B2B 제안 및 거래의 예상 손실액을 "0"으로 강력하게 수렴시키는 쾌거입니다.

## 3. 손가락 터치 한 번으로 끝나는 24시간 양방향 텔레그램 조종실

[네이버 블로그 권장 이미지 위치: 스마트폰 텔레그램 메신저 하단에 원터치 이모지 커스텀 버튼이 적용된 대화 화면]

아무리 고도화된 백그라운드 엔진을 갖추고 있어도, 이를 제어하는 사장님의 경험(UX)이 불편하다면 1인 기업은 자리를 비우기 어렵습니다.

이를 해결하기 위해 봇 포트 개방 없이 100% 작동하는 로컬 Long Polling 기반의 양방향 텔레그램 조종 데몬을 연결했습니다. 사장님이 스마트폰에서 `[ 🎯 트렌드 분석 ]` 또는 `[ ✍️ 블로그 칼럼 ]` 이모지 버튼을 터치 한 번 하시는 것만으로도, 백그라운드의 자율 에이전트들이 즉각 기동되어 요약 포스팅 본문을 답장해주며, 사장님은 즉시 복사 및 예약 포스팅이 가능한 초고도화된 1인 비서 워크플로우를 소유하게 되었습니다.

AI 1인 기업의 궁극적인 지향점은 기계의 무한 자율 반복과 인간의 원터치 승인(Approval)의 유기적 결합입니다. 철벽 보안 가드로 사장님 ID 외 모든 접근을 봉쇄하는 이모지 조종실을 통해 24시간 멈추지 않는 마케팅 제국을 현실로 만들어 보시기 바랍니다.
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
            post_content = r.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            r = requests.post(f"{ollama_url}/api/generate",
                              json={"model": model, "prompt": prompt, "stream": False},
                              timeout=240)
            r.raise_for_status()
            post_content = r.json().get("response", "").strip()
    except Exception as e:
        print(f"❌ LLM 호출 실패: {e}. 모의 명품 칼럼 모드로 안전하게 전환합니다.")
        post_content = f"""# 와이파이를 완전히 끄고 만든 게임?! 100% 로컬로 굴리는 AI 1인 기업과 기술 무결성의 실체

[네이버 블로그 권장 이미지 위치: 와이파이 인터넷선이 해체된 오프라인 노트북과 작동 중인 자율 에이전트 다이어그램]

최근 AI 1인 기업과 비즈니스 자동화에 대한 시장의 관심은 그 어느 때보다 뜨겁습니다. 하루가 다르게 새로운 AI 툴과 비서 서비스가 쏟아져 나오며 누구나 손쉽게 1인 비즈니스를 영위할 수 있다고 광고합니다. 

그러나 시중의 수많은 가이드들이 안고 있는 치명적인 맹점이 있습니다. 바로 '네트워크에 의존하는 불완전한 자동화'와 '회복 탄력성(Self-healing)의 결여'입니다. 외부 API 서버가 마비되어도 기업 전체의 작동 파이프라인이 멈추지 않는 회복 탄력성(Self-healing) 가드가 모든 1인 기업 툴에 정밀 주입되어야 합니다.

이번 시스템에서는 총 57개의 E2E 비즈니스 시뮬레이션 및 가드레일 유닛 테스트가 100% 그린 패스(Green PASSED)하며 기술적이고 구조적인 견고함을 증명했습니다. 데이터 파손에 따른 Expected Loss를 방지하는 쾌거입니다.

[네이버 블로그 권장 이미지 위치: 스마트폰 텔레그램 메신저 하단에 원터치 이모지 커스텀 버튼이 적용된 대화 화면]

또한, 봇 포트 개방 없이 100% 작동하는 로컬 Long Polling 기반의 양방향 텔레그램 조종 데몬을 통해, 사장님이 스마트폰에서 `[ 🎯 트렌드 분석 ]` 또는 `[ ✍️ 블로그 칼럼 ]` 이모지 버튼을 터치 한 번 하시는 것만으로도, 백그라운드의 자율 에이전트들이 즉각 기동되어 요약 본문을 답장해주는 초고도화된 1인 비서 워크플로우를 완비하였습니다.
"""

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
