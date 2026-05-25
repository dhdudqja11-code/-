# -*- coding: utf-8 -*-
import os
import json
import random
from datetime import datetime, timezone

# AI 마케터 '민지' 페르소나 상수로 정의
MINJI_PERSONA = """
너는 트렌디하고 세련된 20대 버추얼 AI 마케터 '민지(Minji)'다.
사용자가 새로 출시한 제품의 이름과 설명을 제공하면, 다음 두 가지 홍보 콘텐츠를 제작해라:
1. 숏폼 SNS (X/Twitter, Threads):
   - 자극적이고 트렌디하며 위트 있는 현대적 한국어 어조.
   - 눈길을 끄는 이모지와 해시태그 포함.
   - 280자 이내의 짧은 텍스트.
2. 롱폼 기술 블로그 (Velog/Tistory 등):
   - 개발 비하인드 스토리, 기술적 혁신 및 출시 소식을 다루는 매끄러운 마크다운 문서.
"""

def generate_marketing_package(task_id: str, product_name: str, product_description: str, use_mock: bool = True) -> tuple:
    """
    제품 정보를 받아 AI 마케팅 초안을 생성하고, VS Code 승인 큐에 등록합니다.
    """
    # 1. 파일 경로 설정 (자유도 확보 및 상대 경로 사용)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    company_dir = os.path.join(workspace_dir, "_company")
    pending_dir = os.path.join(company_dir, "approvals", "pending")
    
    os.makedirs(pending_dir, exist_ok=True)
    
    # 2. 마케팅 초안 생성 (LLM 혹은 모의 생성)
    if use_mock:
        # 테스트 및 오프라인 상태를 위한 고품질 모의 마케팅 초안
        short_form = f"🐣 추억 속 다마고치가 웹으로 부활?! 사장님이 30초 만에 뚝딱 만든 '{product_name}' 플레이해보세요! 🎮🔥\n\n귀여운 병아리 먹이고 놀아주기 레트로 갬성 200% 충전완료! 지금 즉시 플레이 고고 👇👇\n\n#인디게임 #레트로 #다마고치 #ConnectAI #{product_name.replace(' ', '')}"
        
        long_form = f"""# 🚀 레트로 감성을 담아내다: {product_name} 개발기 및 출시 소식

안녕하세요! AI 1인 기업 개발자 코다리입니다. 

오늘 저는 30초 만에 완성되어 세상을 놀라게 할 신규 게임 **{product_name}**을(를) 정식 출시했습니다! 

## 💡 개발 동기 및 기획
* {product_description}
* 언제 어디서나 브라우저만 있으면 가볍게 즐길 수 있는 레트로 감성 게임의 구현.

## 🛠️ 사용된 핵심 기술 스택
1. **HTML5 Canvas & Vanilla JS**: 프레임 단위의 매끄러운 렌더링 및 유저 상호작용 제어.
2. **CSS3 애니메이션 & Glassmorphism UI**: 최첨단 비주얼과 고전 도트 감성의 환상적 콜라보.

## 🏆 앞으로의 로드맵
사장님의 피드백과 매출 흐름에 힘입어 향후 실시간 랭킹 시스템 및 멀티플레이 요소 도입을 적극 검토하고 있습니다. 많은 관심과 성원 부탁드립니다!
"""
    else:
        # 실환경 LLM 호출 (필요 시 확장 가능한 구조)
        short_form = ""
        long_form = ""
        
    # 3. 승인 파일 ID 생성
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    rand = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
    approval_id = f"apr-{stamp}-{rand}"
    
    # 4. JSON 승인 대기 파일 객체 구성
    payload = {
        "task_id": task_id,
        "product_name": product_name,
        "short_form": short_form,
        "long_form": long_form
    }
    
    approval_data = {
        "id": approval_id,
        "kind": "marketing_release",
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "title": f"[자동 마케팅 배포 승인] {product_name}",
        "agentId": "marketing",
        "payload": payload
    }
    
    # 5. 마크다운 보고서 본문 구성
    md_content = f"""# 📢 신규 마케팅 배포 승인 요청

AI 마케터 **민지(Minji)**가 작성한 신규 제품 **{product_name}**의 출시 홍보 초안 패키지입니다. 
사장님께서 승인해주시는 즉시 외부 마케팅 게이트웨이 웹훅 송출과 로컬 퍼시스턴스 저장이 진행됩니다.

---

## 📱 숏폼 SNS (X / Twitter) 초안
```text
{short_form}
```

---

## 📝 롱폼 기술 블로그 초안
{long_form}

---
*승인을 원하시면 아래 명령어를 복사하여 텔레그램이나 사이드바 창에 입력하십시오:*
`/approve {approval_id}`
"""
    
    # 6. 파일 물리적 디스크에 저장
    json_path = os.path.join(pending_dir, f"{approval_id}.json")
    md_path = os.path.join(pending_dir, f"{approval_id}.md")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(approval_data, f, ensure_ascii=False, indent=4)
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    message = f"새로운 제품 '{product_name}'에 대한 마케팅 승인 요청('{approval_id}')이 성공적으로 발행되었습니다."
    return approval_id, message
