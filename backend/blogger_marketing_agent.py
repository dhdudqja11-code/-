#!/usr/bin/env python3
"""
글로벌 마케팅 영업 사원 AI (blogger_marketing_agent.py)
역할: 매일 새벽 구글 검색 최적화(SEO)를 위한 영어 위로 칼럼을 자동 생성하고 블로그스팟에 업로드합니다.
"""

import os
import json
import datetime
import random
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==============================================================================
# 🚨 사장님 필수 세팅 영역 🚨
# 아래 BLOG_ID 변수에 사장님의 구글 블로그스팟 ID를 적어주세요. (숫자로 된 고유 ID)
# ==============================================================================
BLOG_ID = "여기에_블로그스팟_ID를_입력하세요"
# ==============================================================================

# 구글 API 권한 설정 (Blogger 작성 권한)
SCOPES = ['https://www.googleapis.com/auth/blogger']
HERE = os.path.dirname(os.path.abspath(__file__))

def get_blogger_service():
    """구글 OAuth2 인증을 거쳐 Blogger API 서비스 객체를 반환합니다."""
    creds = None
    token_path = os.path.join(HERE, 'blogger_token.json')
    credentials_path = os.path.join(HERE, 'credentials.json')

    # 기존에 로그인한 토큰이 있으면 불러옴
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 토큰이 없거나 만료되었으면 새로 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print("❌ [오류] credentials.json 파일이 없습니다.")
                print("구글 클라우드 콘솔에서 데스크톱 앱용 OAuth 클라이언트 ID를 발급받아 backend 폴더에 넣어주세요.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 새 토큰 저장
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('blogger', 'v3', credentials=creds)

def generate_blog_content():
    """OpenAI GPT-4o를 사용하여 고품질 영어 블로그 콘텐츠(HTML)를 생성합니다."""
    # 환경변수에 있는 OPENAI_API_KEY 사용
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ [오류] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return None, None
        
    client = OpenAI(api_key=api_key)
    
    topics = [
        "How to cope with burnout in your 30s",
        "Finding peace after a difficult breakup",
        "Overcoming late-night anxiety and depression",
        "Why it's okay to not be okay right now",
        "Healing from toxic relationships"
    ]
    selected_topic = random.choice(topics)
    
    prompt = f"""
    You are a top-tier empathetic counselor and an expert copywriter.
    Write a comforting, deeply emotional blog post (in English) targeting the keyword/topic: "{selected_topic}".
    
    Requirements:
    1. Title: Catchy, comforting, and highly optimized for SEO.
    2. Content: A 3-4 paragraph empathetic article that provides genuine comfort.
    3. Formatting: Output the content in pure HTML format (using <h2>, <p>, <strong> tags). DO NOT wrap in ```html markdown blocks.
    4. Call to Action (CTA): At the very end of the post, add a soothing CTA highlighting our service. 
       Use the link "https://global-letters.com" (or your actual domain) and encourage them to get a customized AI prescription letter to heal their heart.
       Make the CTA look beautiful in HTML (e.g., inside a blockquote or a styled div).
    
    Return the result strictly as a JSON object with two keys: "title" and "html_content".
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("title"), result.get("html_content")
    except Exception as e:
        print(f"❌ [오류] OpenAI 콘텐츠 생성 실패: {e}")
        return None, None

def post_to_blogspot(title, content):
    """Blogger API를 사용해 블로그스팟에 글을 발행합니다."""
    if BLOG_ID == "여기에_블로그스팟_ID를_입력하세요":
        print("❌ [오류] BLOG_ID가 설정되지 않았습니다. 스크립트 상단의 BLOG_ID 변수를 사장님의 블로그 ID로 변경해주세요.")
        return

    service = get_blogger_service()
    if not service:
        return

    posts = service.posts()
    body = {
        "title": title,
        "content": content,
        "labels": ["Healing", "Mental Health", "Empathy", "Burnout Recovery"]
    }

    try:
        # isDraft=False 로 설정하면 즉시 대중에게 공개(발행)됩니다.
        request = posts.insert(blogId=BLOG_ID, body=body, isDraft=False)
        response = request.execute()
        print(f"✅ [성공] 블로그 자동 발행 완료! URL: {response.get('url')}")
    except Exception as e:
        print(f"❌ [오류] 블로그 발행 실패: {e}")

def main():
    print("=" * 60)
    print(f"🤖 [마케팅 AI 에이전트] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("글로벌 블로그스팟 포스팅(영어) 작업을 시작합니다.")
    print("=" * 60)
    
    print("1. 구글 SEO 최적화 영어 콘텐츠 생성 중 (OpenAI GPT-4o)...")
    title, content = generate_blog_content()
    
    if not title or not content:
        print("포스팅 작업을 중단합니다.")
        return
        
    print(f"   -> 생성된 제목: {title}")
    
    print("2. 구글 블로그스팟에 자동 발행 중...")
    post_to_blogspot(title, content)
    print("🎉 [마케팅 AI] 오늘의 자동 영업 뛰기가 모두 완료되었습니다!")

if __name__ == '__main__':
    main()
