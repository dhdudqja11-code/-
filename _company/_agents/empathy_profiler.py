#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧠 마음을 묻다 (Ask Your Heart) - 공감 프로파일러 에이전트 (Empathy Profiler Agent)
작성자: Antigravity (풀스택 AI 에이전트)
목적: 사연자가 접수한 사연 텍스트를 심도 깊게 분석하여 5대 감정 지표를 수치화(0.0 ~ 1.0)하고,
      사연자의 방어기제와 핵심 고민 포인트를 요약하여, 메인 AI가 참고할 '처방 가이드라인'을 JSON 형태로 도출합니다.
      OpenAI 연동 불가 혹은 오프라인 환경 시 로컬 심리 분석 템플릿 Fallback 엔진이 구동됩니다.
"""

import os
import re
import json
import sys
import urllib.request
import urllib.error

# Windows cp949 UnicodeEncodeError 방지용 입출력 가드
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def extract_profile_fallback(story):
    """
    OpenAI API를 사용할 수 없는 경우 가동되는 규칙 기반 로컬 심리 분석 Fallback 엔진.
    사연 내 특정 어휘를 카운팅 및 분석하여 감정 점수를 지능적으로 가중 부여합니다.
    """
    # 5대 감정 기본값 세팅
    emotions = {
        "anxiety": 0.40,        # 불안
        "helplessness": 0.30,   # 무기력
        "self_blame": 0.30,     # 자책
        "sadness": 0.40,        # 슬픔
        "loneliness": 0.30      # 고독
    }
    
    # 1. 키워드 매칭을 통한 정밀 가중치 조율
    story_clean = story.lower()
    
    # 불안 점수 보정
    anxiety_kws = ["불안", "미래", "걱정", "앞날", "어쩌지", "준비", "취업", "면접", "시험", "두렵"]
    for kw in anxiety_kws:
        if kw in story_clean:
            emotions["anxiety"] = min(emotions["anxiety"] + 0.15, 1.0)
            
    # 무기력 점수 보정
    helplessness_kws = ["무기력", "피곤", "지친", "번아웃", "의욕", "아무것도", "포기", "쉬고", "지쳐"]
    for kw in helplessness_kws:
        if kw in story_clean:
            emotions["helplessness"] = min(emotions["helplessness"] + 0.15, 1.0)
            
    # 자책 점수 보정
    self_blame_kws = ["자책", "바보", "부족", "실수", "내 탓", "잘못", "한심", "부끄럽", "후회"]
    for kw in self_blame_kws:
        if kw in story_clean:
            emotions["self_blame"] = min(emotions["self_blame"] + 0.20, 1.0)
            
    # 슬픔 점수 보정
    sadness_kws = ["슬픔", "눈물", "우울", "아픔", "상처", "힘들", "괴롭", "힘드", "아프"]
    for kw in sadness_kws:
        if kw in story_clean:
            emotions["sadness"] = min(emotions["sadness"] + 0.15, 1.0)
            
    # 고독 점수 보정
    loneliness_kws = ["고독", "혼자", "외롭", "아무도", "단 둘", "위로", "얘기", "소외", "곁에"]
    for kw in loneliness_kws:
        if kw in story_clean:
            emotions["loneliness"] = min(emotions["loneliness"] + 0.15, 1.0)

    # 2. 가장 높은 수치를 바탕으로 코어 고민 포인트 및 방어기제 조합
    max_emotion = max(emotions, key=emotions.get)
    
    if max_emotion == "self_blame":
        defense_mechanism = "자기에게로의 전향 (Turning against self) 및 내면화"
        core_pain_point = "자신의 실수나 현실의 한계를 고스란히 자책으로 승화하여 정신적 압박감이 가중된 상태"
        prescription_guideline = "섣부른 해결책이나 '더 잘해야 한다'는 계발식 훈계는 치명적인 자책을 유발하므로 절대 피하십시오. 사연자의 부족함이 아니라, 너무 오래 성실히 버텨왔기 때문에 지친 것임을 알리며 그의 고통을 100% 수용하고 자애로운 태도로 위로하십시오."
    elif max_emotion == "anxiety":
        defense_mechanism = "합리화 및 주지화 (Intellectualization)를 통한 두려움 억제"
        core_pain_point = "미래에 대한 불확실성과 현실적 제약에서 오는 불안감으로 인해 인지적 에너지가 고갈된 상태"
        prescription_guideline = "불안의 실체를 규명하려 하거나 '괜찮아질 것이다'라는 막연한 낙관론 대신, '멈추어 서서 바람을 쐬는 시간조차 성장의 일부'라는 관점 전환(Reframing)을 이식하여 사연자의 마음에 안전 지대를 확보해 주십시오."
    elif max_emotion == "helplessness":
        defense_mechanism = "회피 (Avoidance) 및 체념을 통한 에너지 보존"
        core_pain_point = "번아웃과 체력적/정신적 방전으로 인해 스스로 상황을 개선할 의지마저 상실된 심한 피로 상태"
        prescription_guideline = "무언가를 '해야 한다'는 모든 능동 행동 지침을 완전히 배제하십시오. 오로지 '지금은 푹 쉬어도 괜찮은 정당한 쉼의 시간'임을 확언하며, 따뜻한 차 한 잔을 마시는 아날로그식 작은 위안만을 넌지시 권하십시오."
    else:
        defense_mechanism = "억압 (Repression) 및 감정의 격리"
        core_pain_point = "깊은 우울감 혹은 타인과의 소외감으로 인해 자신의 마음을 알아주는 통로가 닫힌 상태"
        prescription_guideline = "사연자의 마음에 등불을 켜주는 따뜻하고 감성적인 은유(예: 겨울 밤의 가로등, 지붕 등)를 적극 차용하십시오. 혼자가 아니며, 사연자의 이야기를 오롯이 품어 안아주고 지지하는 사람이 여기에 있음을 강하게 확신시켜 주십시오."

    return {
        "emotions": {k: round(v, 2) for k, v in emotions.items()},
        "defense_mechanism": defense_mechanism,
        "core_pain_point": core_pain_point,
        "prescription_guideline": prescription_guideline
    }

def extract_profile_openai(story, api_key):
    """
    OpenAI GPT-4o-mini 엔진을 통해 사연자의 내면 심리를 다차원 분석하고 JSON을 리턴합니다.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = (
        "당신은 초엘리트 심리 프로파일러이자 감정 분석 마스터입니다. "
        "다음 사연자의 고민 글을 깊이 있게 읽고, 사연자의 내면 심리를 분석하여 "
        "반드시 하단의 JSON 규격에 맞게만 답변해 주십시오. "
        "마크다운 코드 블록(```json)이나 군더더기 텍스트는 일절 출력하지 말고 순수 JSON 문자열만 즉시 반환하십시오.\n\n"
        "JSON 응답 규격:\n"
        "{\n"
        "  \"emotions\": {\n"
        "    \"anxiety\": 0.85,       // 불안 수치 (0.0 ~ 1.0)\n"
        "    \"helplessness\": 0.70,  // 무기력 수치 (0.0 ~ 1.0)\n"
        "    \"self_blame\": 0.90,    // 자책 수치 (0.0 ~ 1.0)\n"
        "    \"sadness\": 0.60,       // 슬픔 수치 (0.0 ~ 1.0)\n"
        "    \"loneliness\": 0.50     // 고독 수치 (0.0 ~ 1.0)\n"
        "  },\n"
        "  \"defense_mechanism\": \"사연자가 겪는 주요 방어기제 한글 기입 (예: 내면화, 회피 등)\",\n"
        "  \"core_pain_point\": \"사연자의 핵심 아픔/통점 1문장 요약\",\n"
        "  \"prescription_guideline\": \"메인 AI 오영범 마스터가 위로 편지를 쓸 때 극적인 위로 효과를 내기 위해 반드시 지켜야 할 맞춤형 글쓰기 가이드라인 (예: 훈계조 절대 배제, 관점 전환 Reframing 삽입 등 2문장 내외)\"\n"
        "}\n\n"
        f"사연 내용:\n{story}"
    )
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            raw_content = res_data['choices'][0]['message']['content'].strip()
            
            # 마크다운 백틱 가드 제거
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_content = "\n".join(lines[1:-1]).strip()
                    
            # 파싱 검증
            parsed = json.loads(raw_content)
            
            # 스키마 키 강제 보장
            for key in ["emotions", "defense_mechanism", "core_pain_point", "prescription_guideline"]:
                if key not in parsed:
                    raise KeyError(f"Missing key: {key}")
                    
            return parsed
    except Exception as e:
        sys.stderr.write(f"⚠️ OpenAI 공감 프로파일러 API 호출 실패: {e}\n")
        return extract_profile_fallback(story)

def main():
    if len(sys.argv) < 2:
        # 인자 누락 시 기본 사연 텍스트 제공
        story = "요즘 취업 준비 때문에 미래가 불확실해서 매일 밤 잠도 안 오고 너무 불안해요. 내가 왜 이리 바보 같고 부족한지 한심해서 자책만 듭니다."
    else:
        story = sys.argv[1]
        
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        profile = extract_profile_openai(story, api_key)
    else:
        profile = extract_profile_fallback(story)
        
    # stdout에 깨끗한 JSON 출력
    print(json.dumps(profile, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
