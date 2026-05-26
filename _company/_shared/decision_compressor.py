# -*- coding: utf-8 -*-
"""decision_compressor.py
Rule-based RAG Feed compressor that removes expired (7+ days) or duplicate
niche keyword feeds from decisions.md, archiving them safely to decisions_archive.md.
"""
import os
import re
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

def compress_decisions(decisions_path=None, archive_path=None):
    if not decisions_path:
        decisions_path = os.path.abspath(os.path.join(HERE, "decisions.md"))
    if not archive_path:
        archive_path = os.path.abspath(os.path.join(HERE, "decisions_archive.md"))

    if not os.path.exists(decisions_path):
        print(f"⚠️ decisions.md 파일을 찾을 수 없습니다: {decisions_path}")
        return False

    with open(decisions_path, "r", encoding="utf-8") as f:
        content = f.read()

    # RAG Feed 블록들을 안전하게 파싱하기 위한 정규식
    # 각 블록은 '### 📡 [RAG Feed] trend_sniper' 로 시작하여 다음 헤더(### or ##) 혹은 파일 끝까지 매칭됩니다.
    pattern = r"(### 📡 \[RAG Feed\] trend_sniper 자율 스캔 최신 트렌드 — ([^\n]+)\n(.*?))(?=\n### 📡 \[RAG Feed\]|\n## |$)"
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if not matches:
        print("💡 decisions.md에 압축 대상인 RAG Feed 가 존재하지 않습니다.")
        return True

    active_feeds = []
    expired_feeds = []
    deduplicated_feeds = []
    
    # 틈새 키워드 별 최신 피드를 추적하기 위한 맵
    # { keyword: (timestamp, block_content, match_start, match_end) }
    keyword_map = {}
    
    now = datetime.datetime.now()

    for m in matches:
        full_block = m.group(1)
        time_str = m.group(2).strip()
        body = m.group(3)
        
        # 타임스탬프 파싱 시도
        try:
            timestamp = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # 예외 발생 시 현재 시간 등으로 대체 또는 파싱 패스
            timestamp = now

        # 키워드 추출 (정규식으로 `- **추천 틈새 키워드**: `로컬 AI ...`` 형태 추출)
        kw_match = re.search(r"-\s*\*\*추천 틈새 키워드\*\*:\s*`([^`]+)`", body)
        if kw_match:
            keyword = kw_match.group(1).strip()
        else:
            keyword = "UNKNOWN_KEYWORD"

        # 1. 7일 초과 만료 여부 검사
        if (now - timestamp).days >= 7:
            expired_feeds.append(full_block)
            continue

        # 2. 중복 키워드 검사 (가장 최신 피드 1개만 보존)
        if keyword in keyword_map:
            prev_timestamp, prev_block, _, _ = keyword_map[keyword]
            if timestamp > prev_timestamp:
                # 현재 피드가 더 최신이므로 교체하고 이전 피드는 중복으로 보냄
                deduplicated_feeds.append(prev_block)
                keyword_map[keyword] = (timestamp, full_block, m.start(), m.end())
            else:
                # 이전 피드가 더 최신이므로 현재 피드를 중복으로 보냄
                deduplicated_feeds.append(full_block)
        else:
            keyword_map[keyword] = (timestamp, full_block, m.start(), m.end())

    # 유효한 피드들 목록 구성 (원래 파일에 남아있을 대상)
    active_blocks = [item[1] for item in keyword_map.values()]

    # 제거(정제)될 피드들의 모음 (아카이브로 보낼 대상)
    to_archive = expired_feeds + deduplicated_feeds
    
    # 아카이브 파일에 안전하게 기입
    if to_archive:
        archive_header = ""
        if not os.path.exists(archive_path):
            archive_header = "# 📌 회사 의사결정 RAG 피드 보관함 (Archive)\n\n"
            
        with open(archive_path, "a", encoding="utf-8") as af:
            if archive_header:
                af.write(archive_header)
            for block in to_archive:
                now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                af.write(f"\n\n## 📦 [Archived Feed — {now_str}]\n" + block.strip() + "\n")
        print(f"📦 [RAG 아카이브] {len(to_archive)}개의 과거 RAG 피드를 안전하게 보관함({archive_path})에 백업 등재 완료했습니다!")

    # decisions.md 본체 갱신
    # RAG Feed 가 위치했던 모든 인덱스 범위를 모아서 텍스트에서 걷어냅니다.
    # matches 리스트는 파일 내 순서대로 들어 있으므로, 거꾸로(역순) 문자열을 걷어내면 인덱스 밀림 현상 없이 무결하게 정제됩니다.
    modified_content = content
    for m in reversed(matches):
        start, end = m.start(), m.end()
        modified_content = modified_content[:start] + modified_content[end:]

    # 여러 개의 줄바꿈 공백 정제
    modified_content = re.sub(r"\n{3,}", "\n\n", modified_content).strip()

    # 정제 완료된 modified_content 뒤에 유효 피드(active_blocks)들을 쾌적하게 덧붙여 줍니다.
    if active_blocks:
        active_feeds_text = "\n\n" + "\n\n".join([block.strip() for block in active_blocks])
        modified_content += active_feeds_text

    # decisions.md 덮어쓰기
    with open(decisions_path, "w", encoding="utf-8") as f:
        f.write(modified_content + "\n")
    
    print(f"📡 [RAG 다이어트] decisions.md 메모리를 압축하여 {len(active_blocks)}개의 최신 유효 RAG 피드만 쾌적하게 보존 완료했습니다! (과거 피드 {len(to_archive)}개 백업 격리)")
    return True

if __name__ == "__main__":
    compress_decisions()
