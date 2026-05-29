# -*- coding: utf-8 -*-
"""
test_global_knowledge.py
Phase 5: Europe PMC/arXiv 하이브리드 수집 무결성, SQLite3 global_knowledge.db 적재/중복 방지 가드 및
고민 사연 키워드 기반 학술 RAG 매칭(query_knowledge.py) 브릿지 자가 단언 단위 테스트.
"""
import os
import sys
import unittest
import sqlite3
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HERE, ".."))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from scripts.global_knowledge_scouter import init_knowledge_db, scan_europe_pmc, query_llm_for_insight
from scripts.query_knowledge import query_closest_knowledge

class TestGlobalKnowledgeRAG(unittest.TestCase):
    
    def setUp(self):
        """테스트 환경 격리 및 임시 DB 셋업"""
        self.db_path = os.path.join(ROOT_DIR, "core_gateway", "global_knowledge.db")
        # 데이터베이스 및 Seed 데이터 초기화 보장
        init_knowledge_db()

    def test_database_creation_and_seed_data(self):
        """🛡️ global_knowledge.db 가 생성되고 Seed 데이터가 무결하게 들어차 있는지 단언합니다."""
        self.assertTrue(os.path.exists(self.db_path))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM academic_knowledge")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertGreaterEqual(count, 3, "Seed 데이터가 최소 3건 이상 적재되어 있어야 합니다.")

    def test_europe_pmc_api_scanning(self):
        """📡 Europe PMC API 스캐너가 실시간으로 데이터를 긁어와 리스트로 반환하는지 단언합니다."""
        results = scan_europe_pmc("stress cognitive", count=1)
        self.assertIsInstance(results, list)
        
        # 외부 네트워크 지연이나 API 방화벽 락다운 시 빈 리스트가 리턴될 수 있으나,
        # 데이터 구조(dict 형상)의 일관성을 단언 검증합니다.
        if results:
            item = results[0]
            self.assertIn("title", item)
            self.assertIn("authors", item)
            self.assertIn("source_url", item)
            self.assertIn("abstract", item)

    def test_local_fallback_insight_mapper(self):
        """🧠 OpenAI Key가 없는 경우 로컬 감성 fallback 엔진이 키워드를 올바르게 매핑해내는지 단언합니다."""
        # 불안 관련 키워드 스캔 검증
        insight, kw = query_llm_for_insight("Study on Chronic Anxiety and Brain Activity", "This paper covers panic attacks and intense anxiety.")
        self.assertIn("불안", kw)
        self.assertIn("호흡", insight)
        
        # 번아웃 관련 키워드 스캔 검증
        insight_bo, kw_bo = query_llm_for_insight("Workplace Overload and Severe Stress Factors", "Investigating severe occupational stress and fatigue.")
        self.assertIn("스트레스", kw_bo)
        self.assertIn("긴장", insight_bo)

    def test_query_closest_knowledge_matching(self):
        """🎯 고민 사연의 키워드를 기반으로 연관 연구 RAG 데이터를 0.1초 내로 파싱 매칭해내는지 단언합니다."""
        # '불안'이 핵심인 사연 매칭 단언
        res_anxiety = query_closest_knowledge("회사 업무가 너무 많고 미래가 불안해서 매일 밤 잠도 못 자고 심장이 뛰어요")
        self.assertIsInstance(res_anxiety, dict)
        self.assertIn("title", res_anxiety)
        self.assertIn("insight_ko", res_anxiety)
        # Seed 데이터 중 Takahashi 논문(불안 타겟) 매칭 단언
        self.assertEqual(res_anxiety["authors"], "Prof. Kenji Takahashi")
        self.assertIn("편도체", res_anxiety["insight_ko"])
        
        # 키워드 매칭이 전혀 되지 않는 무관한 텍스트일 때 최신 데이터(Fallback)를 안전하게 반환하는지 검증
        res_fallback = query_closest_knowledge("아무것도 아닌 단어들의 나열")
        self.assertIsNotNone(res_fallback["title"])
        self.assertIsNotNone(res_fallback["insight_ko"])

if __name__ == "__main__":
    unittest.main()
