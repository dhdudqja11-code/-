# -*- coding: utf-8 -*-
"""decision_compressor.py
Rule-based RAG Feed & Boss Feedback compressor that removes expired (7+ days)
or duplicate feeds, consolidates raw feedback logs into dense, categorized master rules,
and archives verbose raw records safely to decisions_archive.md.
"""
import os
import sys
import re
import datetime

# Windows 환경 한글 및 이모지 입출력 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))

# 3대 핵심 카테고리 분류용 키워드
KEYWORDS_CAT1 = ['모델', 'KPI', '전략', '수익', '포지셔닝', '영업', '판매', '비즈니스', '플랜', '보험', 'B2B', '가치', '가치 제안', '손실액', '회피 비용', 'ALV', '시뮬레이션', '손실', 'Pricing', '시장']
KEYWORDS_CAT2 = ['디자인', '그리드', '테마', '감성', 'UX', 'UI', '시각', '게이지', '색상', '톤앤매너', '페이지', '랜딩', '공포', '해결책', '대본', '카피', '썸네일', '글꼴', '배색', '서명', '장식', '브로셔']
KEYWORDS_CAT3 = ['시스템', '자동화', 'AI', 'OOM', '컨텍스트', 'API', '게이트웨이', '미들웨어', '감사', '로그', '트랜잭션', 'Audit', 'Gateway', '통신', 'TLS', 'WebSockets', 'JWT', '테스트', 'E2E', 'SHA-256', '해싱', '보안', '서버', 'FastAPI', '구동', '인프라', '개발', '아키텍처', '빌드', 'CI']

def get_words(text):
    """한글, 영문, 숫자를 포함하는 단어 토큰들을 세트로 추출합니다."""
    return set(re.findall(r'[a-zA-Z0-9가-힣]+', text))

def are_similar_rules(rule1, rule2):
    """단어 오버랩 계수(Overlap Coefficient >= 70%)를 활용해 두 규칙의 유사의존성을 식별합니다."""
    words1 = get_words(rule1)
    words2 = get_words(rule2)
    if not words1 or not words2:
        return False
    intersection = words1.intersection(words2)
    overlap = len(intersection) / min(len(words1), len(words2))
    return overlap >= 0.70

def categorize_rule(rule):
    """키워드 빈도를 스코어링하여 규칙을 3대 핵심 마스터 가이드 카테고리 중 하나로 할당합니다."""
    score1 = sum(1 for kw in KEYWORDS_CAT1 if kw in rule)
    score2 = sum(1 for kw in KEYWORDS_CAT2 if kw in rule)
    score3 = sum(1 for kw in KEYWORDS_CAT3 if kw in rule)
    
    max_score = max(score1, score2, score3)
    if max_score == 0:
        return 3  # 기본값: 기술 및 운영 자동화
    if max_score == score3:
        return 3
    if max_score == score1:
        return 1
    return 2

def parse_decisions_file(content):
    """decisions.md 파일을 파싱하여 마스터 상단 가이드라인, 기타 세션별 불릿 규칙, RAG 피드 매치 목록으로 분리합니다."""
    # RAG Feed 블록을 정규식으로 안전하게 선 추출 및 격리
    pattern = r"(### 📡 \[RAG Feed\] trend_sniper 자율 스캔 최신 트렌드 — ([^\n]+)\n(.*?))(?=\n### 📡 \[RAG Feed\]|\n## |$)"
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    content_no_rag = content
    for m in reversed(matches):
        start, end = m.start(), m.end()
        content_no_rag = content_no_rag[:start] + content_no_rag[end:]
        
    lines = content_no_rag.splitlines()
    
    title = "# 📌 회사 핵심 의사결정 로그 (압축본)"
    master_bullets = {1: [], 2: [], 3: []}
    other_bullets = []
    
    current_section = None
    master_key = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            title = stripped
        elif stripped.startswith("## 1."):
            current_section = "master"
            master_key = 1
        elif stripped.startswith("## 2."):
            current_section = "master"
            master_key = 2
        elif stripped.startswith("## 3."):
            current_section = "master"
            master_key = 3
        elif stripped.startswith("## ") or stripped.startswith("### "):
            current_section = "other"
            master_key = None
        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_content = stripped[2:].strip()
            if current_section == "master":
                master_bullets[master_key].append(bullet_content)
            elif current_section == "other":
                other_bullets.append(bullet_content)
                
    return title, master_bullets, other_bullets, matches

def compress_decisions(decisions_path=None, archive_path=None, return_stats=False):
    """decisions.md 파일을 지능적으로 압축 정화하고, 상세 로그를 아카이브로 등재합니다."""
    if not decisions_path:
        decisions_path = os.path.abspath(os.path.join(HERE, "decisions.md"))
    if not archive_path:
        archive_path = os.path.abspath(os.path.join(HERE, "decisions_archive.md"))

    if not os.path.exists(decisions_path):
        print(f"⚠️ decisions.md 파일을 찾을 수 없습니다: {decisions_path}")
        if return_stats:
            return False, {}
        return False

    with open(decisions_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_line_count = len(content.splitlines())

    # 1. decisions.md 파싱
    title, master_bullets, other_bullets, matches = parse_decisions_file(content)

    # 2. RAG Feed 블록 처리 (기존 7일 초과 만료 및 키워드별 최신성 중복 제거 유지)
    active_feeds = []
    expired_feeds = []
    deduplicated_feeds = []
    keyword_map = {}
    now = datetime.datetime.now()

    for m in matches:
        full_block = m.group(1)
        time_str = m.group(2).strip()
        body = m.group(3)
        
        try:
            timestamp = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = now

        kw_match = re.search(r"-\s*\*\*추천 틈새 키워드\*\*:\s*`([^`]+)`", body)
        if kw_match:
            keyword = kw_match.group(1).strip()
        else:
            keyword = "UNKNOWN_KEYWORD"

        # 7일 만료 검사
        if (now - timestamp).days >= 7:
            expired_feeds.append(full_block)
            continue

        # 최신 1개만 중복 제거 보존
        if keyword in keyword_map:
            prev_timestamp, prev_block, _, _ = keyword_map[keyword]
            if timestamp > prev_timestamp:
                deduplicated_feeds.append(prev_block)
                keyword_map[keyword] = (timestamp, full_block, m.start(), m.end())
            else:
                deduplicated_feeds.append(full_block)
        else:
            keyword_map[keyword] = (timestamp, full_block, m.start(), m.end())

    active_blocks = [item[1] for item in keyword_map.values()]
    to_archive_feeds = expired_feeds + deduplicated_feeds

    # 3. 기타 세션 로그 내의 규칙 지침들을 병합 및 고도화
    unique_other_bullets = []
    for r in other_bullets:
        if not r or r.startswith("_세션:") or r.startswith("_최근 압축일"):
            continue
        cleaned = r.strip()
        if cleaned.startswith("- ") or cleaned.startswith("* "):
            cleaned = cleaned[2:].strip()
            
        # 규칙 병합 (유사할 시 더 구체적인 / 긴 지침 보존)
        is_dup = False
        for existing in unique_other_bullets:
            if cleaned == existing:
                is_dup = True
                break
            if are_similar_rules(cleaned, existing):
                is_dup = True
                if len(cleaned) > len(existing):
                    idx = unique_other_bullets.index(existing)
                    unique_other_bullets[idx] = cleaned
                break
        if not is_dup:
            unique_other_bullets.append(cleaned)

    # 병합 완료된 규칙들을 마스터 가이드 카테고리 하단으로 분류 이식 (중복 방지)
    categorized_counts = {1: 0, 2: 0, 3: 0}
    for rule in unique_other_bullets:
        cat = categorize_rule(rule)
        
        # 이미 마스터 가이드에 정의된 룰과 중복 또는 유사한지 검사
        is_master_dup = False
        for mb in master_bullets[cat]:
            if are_similar_rules(rule, mb):
                is_master_dup = True
                break
        if not is_master_dup:
            master_bullets[cat].append(rule)
            categorized_counts[cat] += 1

    # 4. 아카이브할 원본 상세 히스토리 텍스트 추출 (active RAG feed가 전혀 섞이지 않은 content_no_rag을 기준으로 탐색)
    # RAG Feed 추출에 사용된 원본 content의 regex 매치 결과를 활용해 content_no_rag 구성을 재차 보증
    content_no_rag_archive = content
    for m in reversed(matches):
        start, end = m.start(), m.end()
        content_no_rag_archive = content_no_rag_archive[:start] + content_no_rag_archive[end:]

    header_indices = []
    for header in ["## 최근 주요 의사결정 로그", "## [", "## 🚨"]:
        idx = content_no_rag_archive.find(header)
        if idx != -1:
            header_indices.append(idx)
    if header_indices:
        first_other_idx = min(header_indices)
        raw_other_content = content_no_rag_archive[first_other_idx:].strip()
    else:
        raw_other_content = ""

    # 5. 아카이브 파일 안전 백업 기입
    if raw_other_content or to_archive_feeds:
        archive_header = ""
        if not os.path.exists(archive_path):
            archive_header = "# 📌 회사 의사결정 RAG 피드 및 로그 보관함 (Archive)\n\n"
            
        with open(archive_path, "a", encoding="utf-8") as af:
            if archive_header:
                af.write(archive_header)
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if raw_other_content:
                af.write(f"\n\n## 📦 [Archived Raw Log — {now_str}]\n" + raw_other_content + "\n")
            for block in to_archive_feeds:
                af.write(f"\n\n## 📦 [Archived Feed — {now_str}]\n" + block.strip() + "\n")

    # 6. 정화 및 지능형 합산 결과로 decisions.md 재구축
    def format_section(title_text, bullets):
        res = [title_text]
        for b in bullets:
            res.append(f"* {b}")
        return "\n".join(res)

    new_content_lines = []
    new_content_lines.append(title)
    new_content_lines.append("")
    new_content_lines.append(f"_최근 압축일: {datetime.datetime.now().strftime('%Y-%m-%d')}_")
    new_content_lines.append("")
    
    new_content_lines.append(format_section("## 1. 비즈니스 모델 및 전략 방향", master_bullets[1]))
    new_content_lines.append("")
    new_content_lines.append(format_section("## 2. 디자인 및 UX", master_bullets[2]))
    new_content_lines.append("")
    new_content_lines.append(format_section("## 3. 기술 및 운영 자동화", master_bullets[3]))
    
    modified_content = "\n".join(new_content_lines)

    # 최신성 100% RAG Feed들은 맨 하단에 분리 유지
    if active_blocks:
        active_feeds_text = "\n\n" + "\n\n".join([block.strip() for block in active_blocks])
        modified_content += active_feeds_text

    # 7. 파일 안전 갱신 기입
    with open(decisions_path, "w", encoding="utf-8") as f:
        f.write(modified_content + "\n")

    compressed_line_count = len(modified_content.splitlines())
    compression_ratio = 100.0 * (1.0 - (compressed_line_count / max(1, original_line_count)))

    stats = {
        "original_lines": original_line_count,
        "compressed_lines": compressed_line_count,
        "compression_ratio": compression_ratio,
        "archived_feeds_count": len(to_archive_feeds),
        "added_rules_count": sum(categorized_counts.values()),
        "cat1_added": categorized_counts[1],
        "cat2_added": categorized_counts[2],
        "cat3_added": categorized_counts[3]
    }

    try:
        print(f"📡 [RAG 다이어트] decisions.md 메모리 정화 완료: {original_line_count}라인 -> {compressed_line_count}라인 (압축률: {compression_ratio:.1f}%)")
    except Exception:
        # 안전한 콘솔 출력 폴백
        print(f"[RAG Diet] decisions.md compressed successfully from {original_line_count} to {compressed_line_count} lines ({compression_ratio:.1f}% ratio)")
    
    if return_stats:
        return True, stats
    return True

if __name__ == "__main__":
    compress_decisions()
