# -*- coding: utf-8 -*-
"""
test_seo_agent.py
Unit tests for Ask Your Heart - Autonomous SEO Agent and Next.js layout.tsx metadata updater.
"""
import os
import sys
import pytest
import shutil
import tempfile
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HERE, ".."))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scripts.seo_agent import load_reviews, extract_keywords_fallback, extract_keywords_openai, update_nextjs_layout_seo

# 1. reviews.json 로딩 테스트
def test_load_reviews_integration():
    """실제 workspace 내의 reviews.json이 로드되고 데이터가 최소 3개 이상 리스트 구조인지 확인."""
    reviews = load_reviews()
    assert isinstance(reviews, list)
    assert len(reviews) >= 3
    for r in reviews:
        assert "text" in r or "content" in r
        assert "rating" in r

# 2. 로컬 감성/빈도 분석 폴백 엔진 테스트
def test_extract_keywords_fallback_logic():
    """OpenAI API 부재 시의 fallback 엔진이 리뷰 분석 후 중복 없는 3개 키워드를 정상 도출하는지 단언."""
    mock_reviews = [
        {"rating": 5, "text": "요즘 미래에 대한 불안과 취업 스트레스로 너무 우울하고 불면증이 심했는데 도움 되었습니다."},
        {"rating": 5, "text": "회사에서 무기력하고 우울해서 번아웃 온 줄 알았는데 너무 위로가 되네요."},
        {"rating": 5, "text": "불면증 때문에 밤마다 불안했는데 마음이 많이 차분해졌습니다."}
    ]
    
    keywords = extract_keywords_fallback(mock_reviews)
    assert isinstance(keywords, str)
    
    # 쉼표로 구분된 단어 3개 확인
    kw_list = [k.strip() for k in keywords.split(",")]
    assert len(kw_list) == 3
    
    # 도출된 키워드가 한국인 감정 리스트에 있는 유효 키워드인지 확인
    for kw in kw_list:
        assert kw in ["불안", "무기력", "불면증", "우울", "자책", "상처", "취업 준비", "직장", "관계", "번아웃", "스트레스"]

# 3. layout.tsx 메타데이터 정규식 치환 정밀성 테스트
def test_layout_metadata_regex_replacement():
    """Next.js layout.tsx 소스 description 변경 정규식 치환이 깨짐 없이 정확하게 작동하는지 검증."""
    dummy_layout_content = """import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "마음을 묻다 - 당신만의 선명한 빛을 찾아가세요",
  description: "현대인을 위한 AI 심리 처방전. 불안, 무기력, 불면증 등 당신의 아픈 마음을 위로하는 아날로그 편지.",
  robots: {
    index: false,
    follow: false,
  },
};
export default function RootLayout() { return <div>Layout</div> }
"""
    
    test_keywords = "불안, 무기력, 번아웃"
    new_description = f"현대인을 위한 AI 심리 처방전. {test_keywords} 등 당신의 아픈 마음을 위로하는 아날로그 편지."
    
    # re.sub 치환
    updated_content = re.sub(
        r'description:\s*".*?"',
        f'description: "{new_description}"',
        dummy_layout_content
    )
    
    # 치환 완료 확인
    assert f'description: "현대인을 위한 AI 심리 처방전. 불안, 무기력, 번아웃 등 당신의 아픈 마음을 위로하는 아날로그 편지."' in updated_content
    assert 'title: "마음을 묻다' in updated_content  # 다른 속성은 훼손되지 않았는지 단언
    assert 'robots:' in updated_content

# 4. 실물 파일 백업 및 복구를 수반한 E2E layout.tsx 업데이트 테스트
def test_update_nextjs_layout_seo_e2e():
    """실제 layout.tsx 파일을 임시 백업한 후, update_nextjs_layout_seo 호출이 True를 리턴하고 메타 설명이 업데이트되는지 테스트하고 원상복구."""
    possible_paths = [
        os.path.join(ROOT_DIR, 'global-letters', 'src', 'app', 'layout.tsx'),
        os.path.join(os.getcwd(), 'global-letters', 'src', 'app', 'layout.tsx')
    ]
    
    target_path = None
    for path in possible_paths:
        if os.path.exists(path):
            target_path = path
            break
            
    assert target_path is not None, "테스트 실행 환경에 Next.js layout.tsx 파일이 존재해야 합니다."
    
    # 1. 백업 생성
    backup_path = target_path + ".bak"
    shutil.copy2(target_path, backup_path)
    
    try:
        # 2. SEO 갱신 가동
        test_kw = "불안, 번아웃, 관계의 상처"
        success = update_nextjs_layout_seo(test_kw)
        assert success is True
        
        # 3. 갱신 결과 파일 읽어서 단언
        with open(target_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
            
        assert "불안, 번아웃, 관계의 상처" in updated_content
        assert "description:" in updated_content
        
    finally:
        # 4. 원본 파일 원상 복구 및 백업 파일 삭제
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, target_path)
            os.remove(backup_path)
