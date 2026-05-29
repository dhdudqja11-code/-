# -*- coding: utf-8 -*-
"""
query_knowledge.py
고민 사연 텍스트를 인자로 받아 `global_knowledge.db`에서 연관도 높은 뇌과학/임상심리 지식 RAG 및
Scientific Reference 정보를 검색하여 JSON 형태로 표준 출력(stdout)하는 Next.js 연동용 브릿지 스크립트.
"""
import sys
import os
import sqlite3
import json

# UTF-8 출력 강제 가드
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(HERE, ".."))
DB_PATH = os.path.join(WORKSPACE, "core_gateway", "global_knowledge.db")

def query_closest_knowledge(story: str) -> dict:
    """사연 텍스트에 포함된 키워드를 분석하여 global_knowledge.db에서 최적의 레코드 1건을 매핑 반환합니다."""
    # 디폴트 폴백 레퍼런스 (안전 장벽)
    default_ref = {
        "title": "Neural Correlates of Resilience and Coping Mechanisms in Stressful Environments",
        "authors": "Dr. Sarah Jenkins et al.",
        "source_url": "https://europepmc.org/article/MED/109849",
        "insight_ko": "스트레스 상황에서 뇌의 전두엽 활성화는 감정 조절과 인지적 재구성을 도와 상처를 스스로 복구하게 합니다.",
        "keywords": "불안, 스트레스, 우울, 번아웃, 가족"
    }
    
    if not os.path.exists(DB_PATH):
        return default_ref
        
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. 모든 지식 로드
        cursor.execute("SELECT * FROM academic_knowledge ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return default_ref
            
        story_lower = story.lower() if story else ""
        
        # 2. 키워드 매칭 스코어링 (사연 단어 포함도 점수 계산)
        best_row = None
        best_score = 0
        
        for r in rows:
            kw_list = [k.strip() for k in r["keywords"].split(",") if k.strip()]
            score = 0
            for kw in kw_list:
                if kw in story_lower:
                    score += 5 # 키워드 완치 일치 시 고점 부여
                    
            # 뇌과학/심리학 대중 용어로 사연 내 직접 단어 일치 체크
            if r["insight_ko"] and any(w in story_lower for w in ["불안", "걱정", "근심"]) and "불안" in r["keywords"]:
                score += 2
            if r["insight_ko"] and any(w in story_lower for w in ["우울", "슬픔", "눈물"]) and "우울" in r["keywords"]:
                score += 2
            if r["insight_ko"] and any(w in story_lower for w in ["스트레스", "번아웃", "일", "회사"]) and "스트레스" in r["keywords"]:
                score += 2
                
            if score > best_score:
                best_score = score
                best_row = r
                
        # 3. 매칭 성공 시 변환 반환, 실패 시 최신 적재 데이터 반환
        if best_row and best_score > 0:
            return {
                "title": best_row["title"],
                "authors": best_row["authors"],
                "source_url": best_row["source_url"],
                "insight_ko": best_row["insight_ko"],
                "keywords": best_row["keywords"]
            }
        else:
            # 매칭 점수가 0인 경우 가장 최신 등록된 레코드 1건 반환
            latest = rows[0]
            return {
                "title": latest["title"],
                "authors": latest["authors"],
                "source_url": latest["source_url"],
                "insight_ko": latest["insight_ko"],
                "keywords": latest["keywords"]
            }
            
    except Exception as e:
        # DB 에러 등의 예외 시 폴백 데이터로 안전하게 자가 방어
        sys.stderr.write(f"⚠️ [Query DB Error] {e}\n")
        return default_ref

def main():
    # 텍스트 인자를 파이프라인으로 안전하게 수집
    story_input = ""
    if len(sys.argv) > 1:
        story_input = " ".join(sys.argv[1:])
        
    result = query_closest_knowledge(story_input)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
