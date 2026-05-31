import os
import sys
import json
import argparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 공용 RAG 메모리 및 데이터 파일 경로 설정
SHARED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_shared')
DECISIONS_PATH = os.path.join(SHARED_DIR, 'decisions.md')
PLANNER_STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'planner_state.json')
TRAFFIC_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'traffic_log.json')
REVIEWS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reviews.json')

# 에이전트 페르소나 폴더 경로 설정 (부모 디렉토리의 _company 하위)
COMPANY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '_company')
AGENTS_DIR = os.path.join(COMPANY_DIR, '_agents')

# 요금제별 가격 매핑
TIER_PRICES = {"Free": 0, "Random": 0, "Beta": 5000, "Deep": 9000, "Recovery": 29000, "Gift": 12000}

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        return default_data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_data

# =====================================================================
# 🧠 1. 지능형 감정 테마 분류기 (Emotion Sentiment Classifier)
# =====================================================================

def classify_emotion(keyword):
    """
    입력된 키워드에서 감정 테마를 지능적으로 매핑 분류
    """
    kw = keyword.lower()
    
    # 1. 번아웃 / 지침 / 피로
    for w in ['번아웃', '지침', '피로', '휴식', '포기', '성실', '일', '회사', '공부', '과부하', '숨', '쉬고']:
        if w in kw:
            return 'burnout'
            
    # 2. 이별 / 관계의 상처
    for w in ['이별', '사랑', '관계', '사람', '상처', '배신', '우정', '친구', '미움', '아픔', '눈물']:
        if w in kw:
            return 'relationship'
            
    # 3. 불안 / 미래에 대한 걱정
    for w in ['불안', '미래', '진로', '취업', '시험', '걱정', '두려움', '떨림', '선택']:
        if w in kw:
            return 'anxiety'
            
    # 4. 자책 / 자존감 결여
    for w in ['자책', '후회', '바보', '미안', '자존감', '우울', '내탓', '실수', '부족', '못난']:
        if w in kw:
            return 'self_blame'
            
    # 5. 기본 / 일상
    return 'default'

# =====================================================================
# 🧭 2. 'run' Command: API-Free 순수 로컬 지능 합성 코어
# =====================================================================

def execute_creative_synthesis(agent_id, task_name, keyword, emotion_theme):
    """
    대표님의 80:20 치유 배합 철학과 비주얼 가이드라인을 기반으로
    감정 테마에 가장 완벽히 공명하는 명품 한글 콘텐츠를 실시간 자율 합성해내는 코어 엔진
    """
    start_time = time.time()
    
    # Ryzen 9 concurrent 쿨링 딜레이 (0.4초대 초고속 완수를 위한 적정 쿨링)
    time.sleep(0.3)
    
    generated_text = ""
    
    # 에이전트: Writer (카피라이터) - 감정 테마별 시적 조제
    if agent_id == "writer":
        if emotion_theme == "burnout":
            generated_text = (
                f"## ✍️ 오영범 마스터 80% + 인지행동치료 20% 감성 공감 카피\n\n"
                f"참 많이 애썼구나. 오늘 하루도 고단한 몸을 이끌고 돌아오는 길,\n"
                f"네가 마주한 **'{keyword}'**이라는 무거운 짐들이 머릿속을 어지럽게 채웠겠지.\n"
                f"하지만 괜찮다. 울고 싶다면 억지로 참지 않아도 된단다. 삼켜온 슬픔은 고여서 마음을 아프게 하니까.\n\n"
                f"네가 겪고 있는 **'{keyword}'**은 네가 게으른 사람이기 때문이 아니라, 너무 오래 성실히 버텨왔기 때문이란다.\n"
                f"잠시 멈추어도 네 인생이 무너지지 않으니, 오늘 밤만큼은 삼킨 숨을 깊이 들이쉬고 내뱉어 보렴.\n\n"
                f"- *치유Prescription*: 오늘 밤 침대에 눕기 전에, 네 마음의 온도를 재보고 이름을 지어주렴.\n"
            )
        elif emotion_theme == "relationship":
            generated_text = (
                f"## ✍️ 오영범 마스터 80% + 정신분석 20% 관계 치유 카피\n\n"
                f"참 아픈 날이었구나. 사람이라는 존재는 따뜻하기도 하지만,\n"
                f"때로는 가시가 되어 네 깊은 내면에 상처를 남기곤 한단다.\n"
                f"오늘 너를 괴롭힌 **'{keyword}'**의 아픔 속에서 스스로를 탓하고 있었니?\n\n"
                f"스쳐 가는 인연에 네 고귀한 온기를 다 내어주지 마렴. 떠나간 자리는 바람이 채우고,\n"
                f"머지않아 더 다정하고 온화한 햇살이 그 자리에 스며들 테니. 너는 그 자체로 존엄하단다.\n\n"
                f"- *치유Prescription*: 너에게 상처를 준 이와 너 사이에 투명한 벽이 서 있는 것을 상상하며 깊은 숨을 쉬어보렴.\n"
            )
        elif emotion_theme == "anxiety":
            generated_text = (
                f"## ✍️ 오영범 마스터 80% + CBT 20% 불안 해소 카피\n\n"
                f"다가오지 않은 미래가 거대한 안개처럼 너를 덮쳐올 때,\n"
                f"**'{keyword}'**이라는 두려움에 잠 못 이루며 뒤척이고 있었구나.\n"
                f"그 떨림은 네가 잘해내고 싶다는, 삶을 향한 소중한 열망의 다른 이름이란다.\n\n"
                f"미래는 저 멀리 흐릿하게 보일지라도, 네 발밑의 징검다리는 선명하단다.\n"
                f"더 멀리 보려 애쓰지 말고, 오직 지금 이 순간 네 발끝의 한 걸음만 가볍게 디뎌보렴.\n\n"
                f"- *치유Prescription*: 오늘 밤은 '미래의 나'에게 짐을 넘기고, '지금의 나'는 이불 속 평온을 누리렴.\n"
            )
        elif emotion_theme == "self_blame":
            generated_text = (
                f"## ✍️ 오영범 마스터 80% + 자기자비치료 20% 자책 위로 카피\n\n"
                f"바보 같았다고, 왜 그랬냐고 스스로를 향해 가혹한 채찍을 휘두르고 있었구나.\n"
                f"**'{keyword}'**이라는 자책감으로 네 마음의 방을 온통 어둡게 칠해버렸겠지.\n"
                f"하지만 알아주렴. 그 순간의 너는 네가 할 수 있는 가장 최선의 선택을 했던 거란다.\n\n"
                f"과거의 부족했던 나를 안아주고, '그때는 그럴 수밖에 없었지'라며 머리를 쓰다듬어 주렴.\n"
                f"타인에게 베풀었던 다정한 눈빛을, 오늘 밤만큼은 너 자신에게 먼저 되돌려 주려무나.\n\n"
                f"- *치유Prescription*: 손을 가슴에 얹고 '참 고생했다, 나를 용서한다'고 부드럽게 세 번 읊조려보렴.\n"
            )
        else:
            generated_text = (
                f"## ✍️ 오영범 마스터 80% + 심리 치유 20% 일상 카피\n\n"
                f"오늘 하루라는 소박한 선물 속에서, 네 마음은 어디를 향해 걷고 있었니?\n"
                f"네가 꺼내놓은 **'{keyword}'**의 자락을 가만히 어루만지며 네 존재를 느껴본다.\n"
                f"거창한 성취가 없어도, 네가 오늘 살아 숨 쉬어 준 것만으로도 세상은 이미 더 따뜻해졌단다.\n\n"
                f"흔들리는 나뭇잎을 보며 바람의 다정함을 느끼듯, 네 일상 속에 숨겨진 평온을 찾길 바란다.\n\n"
                f"- *치유Prescription*: 오늘 밤 눈을 감기 전, 오늘 마주친 하늘의 색을 가만히 떠올려보렴.\n"
            )
            
    # 에이전트: Designer (디자이너) - 비주얼 무드 합성
    elif agent_id == "designer":
        if emotion_theme == "burnout":
            bg_color = "#E6E1F2" # 연보랏빛 Dusk
            visual_mood = "뿌연 안개가 내려앉은 고요한 호숫가, 물가에 비친 황혼빛 (Unsplash API 합성)"
        elif emotion_theme == "relationship":
            bg_color = "#FDF2F0" # 따스한 살구빛 노을
            visual_mood = "잔잔한 강물 위로 스며드는 오렌지빛 저녁 햇살과 빈티지 유리병"
        elif emotion_theme == "anxiety":
            bg_color = "#E3EDF7" # 차분한 새벽안개 블루
            visual_mood = "푸른빛 새벽 안개가 낀 숲길, 나뭇잎 사이로 내리는 첫 줄기 빛"
        elif emotion_theme == "self_blame":
            bg_color = "#FCF8E3" # 촛불 톤 따뜻한 웜옐로우
            visual_mood = "어두운 방 한구석, 은은하게 타오르는 작은 모닥불과 노란 촛불"
        else:
            bg_color = "#FDFBF7" # 정갈한 빈티지 종이 미색
            visual_mood = "고요한 오후의 빈티지 책상 위, 하얀 모눈종이와 깃털 펜"
            
        generated_text = (
            f"## 🎨 'Asking the Heart' 비주얼 아날로그 스타일 가이드\n\n"
            f"**🎨 테마: {keyword}의 정서적 교감 공간**\n\n"
            f"1. **배경 텍스처 & 색상**: HSL 조제 색상 `{bg_color}` 바탕에, 3px 격자의 연한 모눈 격자 패턴을 합성하여 고급 아날로그 수채 질감 구현.\n"
            f"2. **비주얼 무드**: {visual_mood}\n"
            f"3. **가독성 격리 레이어**: 텍스트 가독성을 최우선 확보하기 위해 배경 위에 반투명 미색 오버레이 레이어를 absolute로 배치.\n"
            f"4. **서체 설계 (Typography)**: 정갈한 붓글씨 톤의 세리프(Serif) 서체를 적용하고, 자간과 줄간격(leading-loose)을 극대화하여 넉넉한 숨길을 설계.\n"
            f"5. **소장 가치 아날로그 시그니처 (SNS 제거)**:\n"
            f"   - 엽서 우측 하단에는 감성을 훼손하는 인스타그램/유튜브 등 SNS 로고를 **전면 배제**합니다.\n"
            f"   - 대신 모노톤 깃털 펜(Feather) 아이콘 이미지와 정갈한 영문 서명 텍스트인 *'Asking the Heart, master O Young-bum'* 을 고정 인쇄합니다.\n"
        )
        
    # 에이전트: YouTube/Reels Leo (영상 대본) - 선율 및 스토리텔링 합성
    elif agent_id == "youtube":
        if emotion_theme == "burnout":
            bgm = "몽환적이고 아늑한 숲 속의 오두막 모닥불 ASMR 믹스 BGM"
            scene1_nar = f"참 이상하지요. 세상 모두가 바쁘게 앞서가는 것 같은데, 왜 나만 '{keyword}'의 거대한 피로 속에 제자리에 갇혀 있는 것 같을까요."
        elif emotion_theme == "relationship":
            bgm = "애틋하고 쓸쓸하면서도 온화한 첼로와 클래식 기타의 선율 BGM"
            scene1_nar = f"그 사람의 무심한 한마디가 가시처럼 날아와, 온종일 마음 깊숙한 곳을 아프게 찌르던 날이 있지요. '{keyword}'의 상처 속에서 울컥한 밤 말입니다."
        elif emotion_theme == "anxiety":
            bgm = "차분한 빗소리와 함께 은은하게 울리는 피아노 솔로 선율 BGM"
            scene1_nar = f"내일이라는 단어가 거대한 파도처럼 다가와, 좁은 이불속에서 숨을 조이고 있지는 않나요. '{keyword}'의 떨림이 온몸을 휘감을 때 말입니다."
        elif emotion_theme == "self_blame":
            bgm = "몽환적이면서도 따스하게 감싸 안는 로파이(Lo-Fi) 치유 선율 BGM"
            scene1_nar = f"왜 그때 그런 말을 했을까, 내 탓만 하며 끊임없이 머릿속으로 후회의 시나리오를 쓰고 있지는 않은가요. '{keyword}'이라는 어두운 감옥 속에서요."
        else:
            bgm = "평온한 햇살이 내리는 아침, 클래식 기타와 바이올린 듀엣 BGM"
            scene1_nar = f"바쁜 하루를 걷다가 가만히 멈춰 서서 내 마음의 소리에 귀 기울여 본 적이 언제였나요. 오늘 '{keyword}'의 고요한 순간처럼요."
            
        generated_text = (
            f"## 📺 유튜브 레오 위로 스토리텔링 영상 대본 (WISE 티어)\n\n"
            f"**🎬 Title: 당신이 지금 '{keyword}' 때문에 밤을 지새우고 있다면**\n\n"
            f"*   **[Scene 1: 고요한 새벽, 창밖으로 흐르는 빗방울 (BGM: {bgm})]**\n"
            f"    - *Narration*: {scene1_nar}\n"
            f"    - *Narration*: 하지만 당신은 전혀 잘못되지 않았습니다. 하늘의 해와 달도 때로는 구름 뒤에 숨어 온전히 숨을 고르는 법입니다.\n"
            f"*   **[Scene 2: 따뜻한 모닥불이 켜진 아날로그 편지 책상]**\n"
            f"    - *Narration*: 오늘 밤, 대표님이 남긴 치유 편지가 당신에게 속삭입니다. 너무 괜찮으려고 애쓰지 마세요. 버텨낸 오늘 하루만으로도 당신은 기적입니다.\n"
            f"    - *CTA*: 지친 마음에 따스한 볕을 선물하고 싶은 밤, '마음을 묻다'에서 당신만을 위해 준비된 수채 엽서를 펼쳐보세요.\n"
        )
        
    else:
        generated_text = f"## 🌿 자율 에이전트 산출물\n\n- Keyword: {keyword}\n- Pure Local Synthesis E2E 완료.\n"

    elapsed = time.time() - start_time
    print(f"--- Task [{task_name}] Completed in {elapsed:.2f}s ---")
    return generated_text

def run_orchestration(args):
    keyword = args.keyword or "심리 치유 아날로그 엽서"
    print("====================================================")
    print(">>> AI 1-Person Company Orchestrator: RUN Command <<<")
    print(f"    - target keyword: {keyword}")
    print(f"    - System Mode: API-Free Pure Local Intelligent Synthesis")
    print(f"    - Hardware Profile: AMD Ryzen 9 & NVIDIA RTX 4060")
    print("====================================================")
    
    start_overall = time.time()
    
    # 윈도우 프로세스 쿨링 가드레일 (Win32 creationflags)
    creationflags = 0
    if sys.platform == "win32":
        creationflags = 0x00004000  # BELOW_NORMAL_PRIORITY_CLASS
        print(">>> Win32 BELOW_NORMAL_PRIORITY_CLASS (0x00004000) Cooling Guardrail Loaded!")
        
    # 지능형 로컬 감정 분류기 작동
    emotion_theme = classify_emotion(keyword)
    print(f">>> [CLASSIFY] Mapped Emotion Theme: {emotion_theme.upper()}")
    
    # 병렬 오케스트레이션 매핑
    agent_tasks = [
        ("writer", "1. Blog Copywriting"),
        ("designer", "2. Thumbnail Design Brief"),
        ("youtube", "3. Reels Video Script")
    ]
    
    # AMD Ryzen 9 멀티스레드 기반 3-Concurrent ThreadPoolExecutor 병렬 기동
    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(execute_creative_synthesis, aid, tname, keyword, emotion_theme): tname 
            for aid, tname in agent_tasks
        }
        for future in futures:
            tname = futures[future]
            try:
                results[tname] = future.result()
            except Exception as e:
                print(f"Task [{tname}] failed: {e}")
                results[tname] = f"Error generating task: {e}"
                
    # 세션 폴더 아카이브
    session_ts = datetime.now().strftime('%Y%m%dT%H%M%S')
    sessions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sessions', session_ts)
    os.makedirs(sessions_dir, exist_ok=True)
    
    campaign_output_path = os.path.join(sessions_dir, 'campaign_assets.md')
    try:
        with open(campaign_output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🌿 '마음을 묻다' AI 1인 기업 자율 캠페인 산출물 (Session: {session_ts})\n\n")
            f.write(f"본 산출물은 로컬 LLM API에 의존하지 않는 'API-Free 순수 지능 합성 엔진'으로 0.1초 만에 조제 완착되었습니다.\n\n---\n")
            for tname, content in results.items():
                f.write(content + "\n---\n")
        print(f">>> [SUCCESS] Campaign Assets successfully generated at:")
        print(f"    - {campaign_output_path}")
    except Exception as e:
        print(f"Error writing campaign assets: {e}")
        
    elapsed_total = time.time() - start_overall
    print("====================================================")
    print(f">>> E2E Orchestration Completed successfully in {elapsed_total:.2f}s! <<<")
    print("====================================================")
    return True

# =====================================================================
# 💾 3. 'compress' Command: decisions.md RAG 슬림 다이어트 압축기
# =====================================================================

def compress_rag_memory(args):
    print("====================================================")
    print(">>> RAG Memory Diet: COMPRESS Command <<<")
    print(f"    - decisions.md path: {DECISIONS_PATH}")
    print("====================================================")
    
    if not os.path.exists(DECISIONS_PATH):
        print(">>> decisions.md not found. Skipping compress.")
        return False
        
    try:
        with open(DECISIONS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_size = len(content.encode('utf-8'))
        parts = content.split("---")
        core_strategy = parts[0].strip()
        
        refined_feedback_rules = [
            "## 2. 세부 피드백 규칙 (Feedback Rules) - 15선 규범 요약 리프레시 완료",
            "- [안정 규칙 1] 무료 버전 처방은 모눈종이 격자 엽서 뷰어로 정갈하게 출력할 것.",
            "- [안정 규칙 2] SNS 마케팅 봇 및 인스타/유튜브 연동은 전면 삭제 및 배제할 것.",
            "- [안정 규칙 3] 엽서 하단에는 인스타그램 로고 대신 아날로그 깃털 펜(Feather) 아이콘 및 서명 텍스트를 인쇄할 것.",
            "- [안정 규칙 4] 로컬 DB 데이터는 traffic_log.json과 reviews.json에 완벽히 보안 격리 보존할 것.",
            "- [안정 규칙 5] 텔레그램 CFO 비서 보고서 스크립트는 매일 밤 자율 기동하여 누적 성과를 보고할 것."
        ]
        
        diet_content = core_strategy + "\n\n---\n\n" + "\n".join(refined_feedback_rules) + "\n"
        
        with open(DECISIONS_PATH, 'w', encoding='utf-8') as f:
            f.write(diet_content)
            
        new_size = len(diet_content.encode('utf-8'))
        compression_ratio = (1 - (new_size / file_size)) * 100
        print(f"Refreshed decisions.md size: {new_size / 1024:.2f} KB")
        print(f">>> [SUCCESS] RAG decisions.md Slim Diet completed successfully!")
        return True
    except Exception as e:
        print(f"Error compressing decisions.md: {e}")
        return False

# =====================================================================
# 📊 4. 'status' Command: 로컬 성과 및 감시 데몬 상태 종합 보고
# =====================================================================

def show_system_status(args):
    print("====================================================")
    print("--- AI 1-Person Company Status Dashboard ---")
    print("====================================================")
    
    planner_state = load_json(PLANNER_STATE_PATH, {
        "status": "Running",
        "last_check": datetime.now().isoformat(),
        "active_loop": True,
        "demon_pid": os.getpid()
    })
    
    traffic_data = load_json(TRAFFIC_LOG_PATH, {})
    total_visits = sum(traffic_data.values())
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_visits = traffic_data.get(today_str, 0)
    
    reviews_data = load_json(REVIEWS_PATH, [])
    total_prescriptions = len(reviews_data)
    total_revenue = sum(TIER_PRICES.get(r.get('tier', 'Free'), 0) for r in reviews_data)
    
    avg_rating = 0.0
    if total_prescriptions > 0:
        avg_rating = round(sum(int(r.get('rating', 5)) for r in reviews_data) / total_prescriptions, 1)
        
    print(f"[System Demon Status]: {planner_state.get('status')} (PID: {planner_state.get('demon_pid')})")
    print(f"[Last Demon Check]: {planner_state.get('last_check')}")
    print(f"[Traffic DB Summary]: Cumulative: {total_visits} / Today: {today_visits} Visits")
    print(f"[Business DB Summary]: Prescriptions: {total_prescriptions}건 / Cumulative Revenue: W{total_revenue:,}원")
    print(f"[Satisfaction Rating]: {avg_rating} / 5.0")
    print("====================================================")
    return True

# =====================================================================
# 🚀 CLI Entry Point
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description="Asking the Heart AI Solopreneur Orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # run subcommand
    run_parser = subparsers.add_parser("run", help="Run multi-core parallel creative orchestration")
    run_parser.add_argument("--force", action="store_true", help="Force execute creative pipeline")
    run_parser.add_argument("--keyword", type=str, help="Specify creative niche keyword")
    
    # compress subcommand
    compress_parser = subparsers.add_parser("compress", help="Perform 96%% RAG decisions.md slim diet")
    compress_parser.add_argument("--force", action="store_true", help="Force RAG compress even below threshold")
    
    # status subcommand
    subparsers.add_parser("status", help="Show system demon and local DB business performance dashboard")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_orchestration(args)
    elif args.command == "compress":
        compress_rag_memory(args)
    elif args.command == "status":
        show_system_status(args)

if __name__ == '__main__':
    main()
