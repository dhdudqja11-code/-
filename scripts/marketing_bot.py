#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
✍️ 마음을 묻다 (Ask Your Heart) - 자율 감성 마케팅 봇 (Marketing Bot)
작성자: Antigravity (풀스택 AI 에이전트)
목적: 별점 5점짜리 정성 리뷰를 발굴하여, 오영범 마스터의 특유의 따뜻하고 묵직한 문체(두괄식 공감, 조용한 위로)로
      인스타그램 홍보 카드뉴스 피드 및 카피라이팅 글을 자율 작지하여 instagram_feed.txt 파일로 보관합니다.
      OpenAI 환경 미비 시, 감성 텍스트 템플릿 생성 엔진(Handcrafted Emotion Generator)이 백업 구동됩니다.
"""

import os
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

def filter_five_star_reviews(reviews):
    """
    별점 5점짜리 리뷰만 필터링하여 감동적인 피드백을 확보
    """
    five_stars = [r for r in reviews if r.get('rating') == 5]
    return five_stars

def generate_feed_fallback(reviews):
    """
    OpenAI API Key가 없거나 오류 시 구동되는 로컬 감성 마케팅 텍스트 템플릿 생성 엔진
    """
    print("ℹ️ 로컬 감성 마케팅 텍스트 템플릿 생성 엔진을 구동합니다.")
    
    quote = "요즘 미래에 대한 불안과 취업 준비 때문에 너무 스트레스 받았는데, 편지를 읽고 정말 따뜻한 위로를 받았습니다."
    if reviews:
        # 무작위로 5점 리뷰 텍스트 채용
        quote = reviews[0].get('text', reviews[0].get('content', quote))
        
    fallback_text = f"""[📸 오늘의 인스타그램 자동 생성 감성 피드]
------------------------------------------------------------
지우님, 텅 빈 방 안에서 홀로 삼켜내야 했던 그 많은 불안의 시간들이 제게도 전해지는 듯하여 마음이 아립니다.

오늘 한 유저분께서 소중한 마음을 배달해 주셨습니다.
" {quote} "

우리는 가끔 세상의 속도에 맞추지 못한다는 생각에 스스로를 모질게 몰아세우곤 합니다.
하지만 겨울 나무가 잎을 다 떨구고 앙상하게 서 있는 것은 결코 죽은 것이 아닙니다. 다가올 찬란한 봄을 위해 보이지 않는 뿌리 깊은 곳에서 조용히 생명력을 비축하고 있는, 가장 치열하고 경이로운 휴식의 시간이지요.

지금 당신이 겪고 있는 무력감과 슬픔 역시, 당신의 영혼이 더 깊어지고 단단해지기 위해 반드시 거쳐야 할 겨울의 한가운데일 뿐입니다. 자신을 탓하지 마세요. 당신은 이미 당신의 존재 자체만으로도 충분히 눈부시고 가치 있는 사람입니다.

오늘 밤은 부디 세상의 소음을 끄고, 스스로의 어깨를 토닥이며 "지금 이대로도 괜찮아"라고 말해주는 밤이 되기를 바랍니다.

- 보낸 이: 오영범 마스터

------------------------------------------------------------
🏷️ Hashtags:
#마음을묻다 #위로글귀 #감성글귀 #인생처방전 #오영범작가 #불안해하지마 #마음챙김 #아날로그엽서
------------------------------------------------------------
"""
    return fallback_text

def generate_feed_openai(reviews, api_key):
    """
    OpenAI GPT-4o를 이용해 마스터 오영범의 따뜻한 문체로 감동 리뷰 기반 마케팅 피드 자동 생성
    """
    print("⚡ OpenAI GPT 지능형 감성 마케팅 봇을 구동합니다.")
    
    # 5점 리뷰 리스트 요약
    review_pool = "\n".join([f"- {r.get('text', r.get('content', ''))}" for r in reviews[:3]])
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = (
        "당신은 오영범 작가(마스터)의 페르소나입니다. "
        "다음은 우리 위로 엽서 서비스의 5점 만점 고객 리뷰들입니다:\n"
        f"{review_pool}\n\n"
        "이 감동적인 리뷰 중 하나 혹은 전체의 흐름을 인용하여, 인스타그램 피드에 올릴 마케팅 문구를 오영범 마스터의 실제 어조로 작성해줘.\n"
        "작성 원칙:\n"
        "1. 존댓말과 따뜻한 아날로그 감성을 결합하라.\n"
        "2. 해결책을 억지로 제시하지 말고 감정의 정당성을 먼저 지지하라.\n"
        "3. 밤, 봄, 비, 꽃, 온기, 하루와 같은 서정적인 비주얼 이미지를 담아라.\n"
        "4. 해시태그 #마음을묻다 #위로글귀 #감성글귀 를 마지막에 반드시 포함하라.\n"
        "5. 카드뉴스 대본으로 읽기 편하게 가독성 높게 줄바꿈을 자주 사용하라."
    )
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body)
            feed_content = res_data['choices'][0]['message']['content'].strip()
            return f"[📸 오늘의 인스타그램 자동 생성 감성 피드]\n------------------------------------------------------------\n{feed_content}\n------------------------------------------------------------"
    except Exception as e:
        print(f"⚠️ OpenAI API 호출 실패: {e}")
        return generate_feed_fallback(reviews)

def main():
    print("============================================================")
    print("✍️ [Marketing Bot] 자율 감성 마케팅 텍스트 기획을 개시합니다.")
    print("============================================================")
    
    reviews = load_reviews()
    five_stars = filter_five_star_reviews(reviews)
    
    print(f"• 전체 리뷰: {len(reviews)}개 / 별점 5점 리뷰: {len(five_stars)}개")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and five_stars:
        feed_text = generate_feed_openai(five_stars, api_key)
    else:
        feed_text = generate_feed_fallback(five_stars)
        
    # 결과 아카이빙 파일 적재
    output_path = os.path.join(os.path.dirname(__file__), '..', 'reports', 'instagram_feed.txt')
    # 폴더가 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(feed_text)
        print(f"✅ [Marketing Bot] 인스타그램 홍보 피드 초안 빌드 완료!")
        print(f"• 저장 경로: {output_path}")
        print("\n" + feed_text[:350] + "...\n(이하 생략)")
    except Exception as e:
        print(f"❌ 아카이브 파일 저장 중 에러: {e}")
        
    print("============================================================")

if __name__ == "__main__":
    main()
