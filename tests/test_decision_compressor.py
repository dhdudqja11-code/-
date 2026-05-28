# -*- coding: utf-8 -*-
import os
import sys
import pytest
import datetime

# _shared 폴더를 sys.path에 추가합니다.
HERE = os.path.dirname(os.path.abspath(__file__))
SHARED_FOLDER = os.path.abspath(os.path.join(HERE, "..", "_company", "_shared"))
if SHARED_FOLDER not in sys.path:
    sys.path.append(SHARED_FOLDER)

import decision_compressor

@pytest.fixture
def temp_decisions_setup(tmp_path):
    """테스트 기동 중 디스크의 실제 decisions.md를 보호하기 위해 격리된 파일 샌드박스를 구성합니다."""
    temp_decisions = tmp_path / "decisions.md"
    temp_archive = tmp_path / "decisions_archive.md"
    
    # 기본 의사결정 마스터 로그 템플릿 적재
    master_template = """# 📌 회사 핵심 의사결정 로그 (테스트)

## 1. 비즈니스 모델 및 전략 방향
* **모델**: 디지털 경험 티켓.
* **KPI**: ITCR.

## 최근 주요 의사결정 로그
- 모든 마케팅 및 영업 자료는 재무적 손실액에 초점을 맞춰야 한다.
"""
    temp_decisions.write_text(master_template, encoding="utf-8")
    
    return temp_decisions, temp_archive

def test_compress_no_duplicates_or_expiry(temp_decisions_setup):
    """[압축기 테스트 - 해피패스] 중복이나 만료가 없는 RAG Feed가 있을 때 훼손 없이 보존되는지 검증합니다."""
    temp_decisions, temp_archive = temp_decisions_setup
    
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    feed_content = f"""

### 📡 [RAG Feed] trend_sniper 자율 스캔 최신 트렌드 — {now_str}
- **추천 틈새 키워드**: `로컬 AI 자동화`
- **추천 썸네일 카피**: "30초 만에 로컬로 AI 가동하는 법"
- **콘텐츠 핵심 테마**: "로컬 AI"
"""
    # 임시 파일에 쓰기
    with open(temp_decisions, "a", encoding="utf-8") as f:
        f.write(feed_content)
        
    # 압축 기동
    result = decision_compressor.compress_decisions(str(temp_decisions), str(temp_archive))
    
    assert result is True
    
    # 검증: 본체 보존 여부
    content = temp_decisions.read_text(encoding="utf-8")
    assert "로컬 AI 자동화" in content
    assert "## 1. 비즈니스 모델 및 전략 방향" in content
    assert "모든 마케팅 및 영업 자료는" in content
    
    # 검증: 아카이브 검증 (마스터 이외의 raw 로그는 아카이브에 이식되고 본체에서 걷혔어야 함)
    assert os.path.exists(temp_archive)
    archive_content = temp_archive.read_text(encoding="utf-8")
    assert "모든 마케팅 및 영업 자료는" in archive_content

def test_compress_deduplication_success(temp_decisions_setup):
    """[압축기 테스트 - 중복 정제] 동일한 키워드로 여러 피드가 쌓였을 때, 최신 1개만 남고 이전은 아카이브로 등재되는지 검증합니다."""
    temp_decisions, temp_archive = temp_decisions_setup
    
    # 2개의 중복 RAG 피드 생성 (과거 피드와 5분 뒤의 최신 피드)
    past_time = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    feeds = f"""

### 📡 [RAG Feed] trend_sniper 자율 스캔 최신 트렌드 — {past_time}
- **추천 틈새 키워드**: `로컬 AI 자동화`
- **추천 썸네일 카피**: "과거 썸네일 카피"
- **콘텐츠 핵심 테마**: "과거 테마"

### 📡 [RAG Feed] trend_sniper 자율 스캔 최신 트렌드 — {now_str}
- **추천 틈새 키워드**: `로컬 AI 자동화`
- **추천 썸네일 카피**: "최신 썸네일 카피"
- **콘텐츠 핵심 테마**: "최신 테마"
"""
    with open(temp_decisions, "a", encoding="utf-8") as f:
        f.write(feeds)
        
    # 압축 기동
    result = decision_compressor.compress_decisions(str(temp_decisions), str(temp_archive))
    
    assert result is True
    
    # decisions.md 본체 검증: 최신 피드만 존재해야 함
    content = temp_decisions.read_text(encoding="utf-8")
    assert "최신 썸네일 카피" in content
    assert "과거 썸네일 카피" not in content
    assert "## 1. 비즈니스 모델 및 전략 방향" in content # 마스터 보존
    
    # decisions_archive.md 백업함 검증: 과거 피드가 들어가 있어야 함
    assert os.path.exists(temp_archive)
    archive_content = temp_archive.read_text(encoding="utf-8")
    assert "과거 썸네일 카피" in archive_content
    assert "최신 썸네일 카피" not in archive_content

def test_compress_expiry_success(temp_decisions_setup):
    """[압축기 테스트 - 만료 정제] 7일이 지난 RAG 피드가 있을 때, 본체에서는 완전히 걷히고 아카이브에 이식되는지 검증합니다."""
    temp_decisions, temp_archive = temp_decisions_setup
    
    # 8일이 지난 만료 피드 생성
    expired_time = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    feed_content = f"""

### 📡 [RAG Feed] trend_sniper 자율 스캔 최신 트렌드 — {expired_time}
- **추천 틈새 키워드**: `오래된 AI 트렌드`
- **추천 썸네일 카피**: "오래된 썸네일"
- **콘텐츠 핵심 테마**: "오래된 테마"
"""
    with open(temp_decisions, "a", encoding="utf-8") as f:
        f.write(feed_content)
        
    # 압축 기동
    result = decision_compressor.compress_decisions(str(temp_decisions), str(temp_archive))
    
    assert result is True
    
    # decisions.md 본체 검증: 오래된 피드는 사라졌어야 함
    content = temp_decisions.read_text(encoding="utf-8")
    assert "오래된 AI 트렌드" not in content
    assert "## 1. 비즈니스 모델 및 전략 방향" in content # 마스터 보존
    
    # decisions_archive.md 백업함 검증: 오래된 피드가 들어가 있어야 함
    assert os.path.exists(temp_archive)
    archive_content = temp_archive.read_text(encoding="utf-8")
    assert "오래된 AI 트렌" in archive_content

def test_compress_boss_feedback_and_consolidation(temp_decisions_setup):
    """[압축기 테스트 - 사장님 피드백 및 분류 압축] 사장님 피드백 및 날짜별 피드백이 마스터 가이드 아래에 병합/분류 및 아카이브되는지 검증합니다."""
    temp_decisions, temp_archive = temp_decisions_setup
    
    # 2개의 날짜별 블록과 사장님 피드백 블록 생성 (중복적인 컴플라이언스 및 디자인 규칙)
    feedback_content = """
## [2026-05-25] [사장님 자율 피드백 피딩] - 실시간 자가 학습 연동
- 모든 API 호출은 반드시 '컴플라이언스 게이트웨이'를 거치도록 아키텍처를 설계한다.
_세션: 2026-05-25 14:00_

## [2026-05-26] [자율 사이클 — 2026-05-26] 1인 기업 24시간 운영 중.
- 모든 API 호출은 반드시 '컴플라이언스 게이트웨이'를 거쳐야 한다.
- 위험 레벨 게이지의 색상과 시각적 강조 효과는 명시된 디자인 스펙을 따른다.
_세션: 2026-05-26 10:00_
"""
    with open(temp_decisions, "a", encoding="utf-8") as f:
        f.write(feedback_content)
        
    # return_stats=True 옵션으로 압축 실행
    success, stats = decision_compressor.compress_decisions(str(temp_decisions), str(temp_archive), return_stats=True)
    
    assert success is True
    assert stats["added_rules_count"] >= 2 # 최소 컴플라이언스 룰 1개 + 디자인 룰 1개가 분류 이식되었어야 함
    
    content = temp_decisions.read_text(encoding="utf-8")
    
    # 1. 중복 병합된 컴플라이언스 룰이 master 3(기술 및 자동화) 섹션 아래에 이식되었는지 검증
    assert "컴플라이언스 게이트웨이" in content
    # 2. 디자인 룰이 master 2(디자인 및 UX) 섹션 아래에 이식되었는지 검증
    assert "위험 레벨 게이지" in content
    
    # 3. 원본 날짜별 헤더들은 본체에서 걷혔어야 함
    assert "[2026-05-25] [사장님 자율 피드백 피딩]" not in content
    assert "[자율 사이클 — 2026-05-26]" not in content
    
    # 4. 아카이브 파일에 원본 상세 로그가 백업되었는지 검증
    assert os.path.exists(temp_archive)
    archive_content = temp_archive.read_text(encoding="utf-8")
    assert "[사장님 자율 피드백 피딩]" in archive_content
    assert "컴플라이언스 게이트웨이" in archive_content

