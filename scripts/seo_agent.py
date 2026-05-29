#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔍 마음을 묻다 (Ask Your Heart) - 자율 SEO 최적화 에이전트 (SEO Agent)
작성자: Antigravity (풀스택 AI 에이전트)
목적: 유저들이 남긴 reviews.json 데이터를 분석하여 가장 고통받고 있는 키워드(우울, 무기력, 번아웃 등)를 
      추출한 뒤 Next.js의 layout.tsx 내 메타 태그(description)를 스스로 자동 수정 업데이트합니다.
      OpenAI 연동 실패 혹은 미지원 환경 시 로컬 감성 분석 엔진(Frequency-Based Fallback Engine)이 백업 구동됩니다.
"""

import os
import re
import json
import urllib.request
import urllib.error
import sys

# Prevent Windows cp949 UnicodeEncodeError when printing emojis/Korean in terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def load_reviews():
    # reviews.json 위치 파악
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'global-letters', 'reviews.json'),
        os.path.join(os.getcwd(), 'global-letters', 'reviews.json'),
        'reviews.json'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 리뷰 파일 로드 실패: {path} - {e}")
    return []

def extract_keywords_fallback(reviews):
    """
    OpenAI API를 사용할 수 없는 경우 작동하는 로컬 빈도수 분석 기반 샌드박스 키워드 추출 엔진
    """
    print("ℹ️ 로컬 감성 분석 엔진(Frequency-Based Fallback Engine)을 백업 구동합니다.")
    text_pool = " ".join([r.get('text', r.get('content', '')) for r in reviews])
    
    # 한국인들이 자주 겪는 감정 고민 리스트
    target_emotions = ["불안", "무기력", "불면증", "우울", "자책", "상처", "취업 준비", "직장", "관계", "번아웃", "스트레스"]
    emotion_counts = {}
    
    for emotion in target_emotions:
        matches = len(re.findall(emotion, text_pool))
        if matches > 0:
            emotion_counts[emotion] = matches
            
    # 정렬하여 가장 빈도 높은 3개 추출
    sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
    top_3 = [item[0] for item in sorted_emotions[:3]]
    
    # 만약 빈도가 하나도 없으면 기본값 적용
    while len(top_3) < 3:
        default_emotions = ["불안", "무기력", "상처"]
        for d in default_emotions:
            if d not in top_3:
                top_3.append(d)
                
    return ", ".join(top_3)

def extract_keywords_openai(reviews, api_key):
    """
    OpenAI GPT-4o API를 통해 정밀하게 최신 감정 트렌드 키워드 3개를 도출
    """
    print("⚡ OpenAI GPT 지능형 엔진을 통해 트렌드 키워드를 도출합니다.")
    review_texts = "\n".join([f"- {r.get('text', r.get('content', ''))}" for r in reviews[-50:]])
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = (
        "다음은 심리 안부/처방 서비스 유저들의 솔직한 후기입니다. "
        "사연자들이 현재 가장 빈번하게 겪고 고통받아 하는 감정 키워드(예: 불안, 무기력, 번아웃 등) 3가지를 "
        "쉼표로만 구분해 정확히 단어 3개만 답변해줘. 단어 이외의 군더더기는 일절 대답하지 마.\n\n"
        f"리뷰 내역:\n{review_texts}"
    )
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            keywords = res_data['choices'][0]['message']['content'].strip()
            # 군더더기 클렌징
            keywords = keywords.replace('"', '').replace("'", "").strip()
            return keywords
    except Exception as e:
        print(f"⚠️ OpenAI API 호출 실패: {e}")
        return extract_keywords_fallback(reviews)

def update_nextjs_layout_seo(keywords):
    # layout.tsx 위치 파악
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'global-letters', 'src', 'app', 'layout.tsx'),
        os.path.join(os.getcwd(), 'global-letters', 'src', 'app', 'layout.tsx'),
        'src/app/layout.tsx'
    ]
    
    target_path = None
    for path in possible_paths:
        if os.path.exists(path):
            target_path = path
            break
            
    if not target_path:
        print("❌ Next.js layout.tsx 파일을 찾지 못해 SEO 업데이트를 취소합니다.")
        return False
        
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_description = f"현대인을 위한 AI 심리 처방전. {keywords} 등 당신의 아픈 마음을 위로하는 아날로그 편지."
        
        # description 정규식 교체 (description: "..." 패턴 대응)
        updated_content = re.sub(
            r'description:\s*".*?"',
            f'description: "{new_description}"',
            content
        )
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print(f"✅ [SEO Agent] Next.js 메타 설명 업데이트 완료!")
        print(f"• 갱신된 SEO 설명글: {new_description}")
        return True
    except Exception as e:
        print(f"❌ Next.js layout.tsx 파일 수정 중 치명적 에러: {e}")
        return False

def main():
    print("============================================================")
    print("🔍 [SEO Agent] 자율 검색엔진 최적화 작업을 개시합니다.")
    print("============================================================")
    
    reviews = load_reviews()
    if not reviews:
        print("ℹ️ 신규 리뷰 내역이 없습니다. 기본 검색 키워드로 SEO 보정을 진행합니다.")
        keywords = "불안, 무기력, 관계 상처"
    else:
        print(f"• 총 {len(reviews)}개의 리뷰 데이터가 로드되었습니다.")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            keywords = extract_keywords_openai(reviews, api_key)
        else:
            keywords = extract_keywords_fallback(reviews)
            
    print(f"🎯 도출된 검색 최적화 핵심 키워드: {keywords}")
    update_nextjs_layout_seo(keywords)
    print("============================================================")

if __name__ == "__main__":
    main()
