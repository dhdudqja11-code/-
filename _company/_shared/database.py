#!/usr/bin/env python3
# version: db_v1
"""Marketing SQLite Database Manager — records campaign histories, audit logs,
and publishing states to establish solid data-driven feedback loops.
"""
import os, sys, sqlite3, time

# Windows 환경 한글 입출력 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "marketing.db")

def get_connection():
    """SQLite DB 연결 객체를 가져오고 테이블이 존재하지 않으면 자동 초기화합니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """테이블 스키마 생성 및 초기화."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. campaigns 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        campaign_dir TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT,
        naver_published INTEGER DEFAULT 0,
        instagram_published INTEGER DEFAULT 0
    )
    """)
    
    # 2. audit_logs 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL
    )
    """)
    
    # 3. posts_metrics 테이블 신설
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        platform TEXT NOT NULL,
        post_identifier TEXT,
        title TEXT,
        url TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        collected_at TEXT NOT NULL,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
    )
    """)
    
    conn.commit()
    conn.close()

def log_campaign(timestamp, campaign_dir, status, error_message=None, naver=0, insta=0):
    """캠페인 가동 이력을 기록합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO campaigns (timestamp, campaign_dir, status, error_message, naver_published, instagram_published) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, campaign_dir, status, error_message, naver, insta)
        )
        conn.commit()
        campaign_id = cursor.lastrowid
        log_audit("SYSTEM", "LOG_CAMPAIGN", f"Campaign recorded: ID {campaign_id} | Dir: {campaign_dir} | Status: {status}")
        return campaign_id
    except Exception as e:
        print(f"⚠️ 캠페인 기록 데이터베이스 에러: {e}")
    finally:
        conn.close()

def log_audit(actor, action, details):
    """행위 감사 로그를 기록합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, actor, action, details) VALUES (?, ?, ?, ?)",
            (timestamp, actor, action, details)
        )
        conn.commit()
    except Exception as e:
        print(f"⚠️ 감사 로그 기록 데이터베이스 에러: {e}")
    finally:
        conn.close()

def get_latest_campaigns(limit=5):
    """최신 캠페인 내역을 가져옵니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM campaigns ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"⚠️ 캠페인 조회 에러: {e}")
        return []
    finally:
        conn.close()

def log_metrics(campaign_id, platform, post_identifier, title, url, views, likes, comments):
    """발행물 지표를 안전하게 영구 적재합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        collected_at = time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO posts_metrics (campaign_id, platform, post_identifier, title, url, views, likes, comments, collected_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (campaign_id, platform, post_identifier, title, url, views, likes, comments, collected_at)
        )
        conn.commit()
        log_audit("SYSTEM", "LOG_METRICS", f"Metrics recorded for {platform}: views={views}, likes={likes} | Title: {title}")
    except Exception as e:
        print(f"⚠️ 지표 기록 데이터베이스 에러: {e}")
    finally:
        conn.close()

def get_performance_summary():
    """지금까지 누적 마케팅 성과 및 베스트 퍼포머를 쿼리하여 반환합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    summary = {
        "naver_views": 0,
        "naver_likes": 0,
        "insta_views": 0,
        "insta_likes": 0,
        "best_performer": None
    }
    try:
        # 네이버 누적 합산
        cursor.execute("SELECT SUM(views) as total_v, SUM(likes) as total_l FROM posts_metrics WHERE platform='naver'")
        row = cursor.fetchone()
        if row and row["total_v"] is not None:
            summary["naver_views"] = row["total_v"]
            summary["naver_likes"] = row["total_l"]

        # 인스타 누적 합산
        cursor.execute("SELECT SUM(views) as total_v, SUM(likes) as total_l FROM posts_metrics WHERE platform='instagram'")
        row = cursor.fetchone()
        if row and row["total_v"] is not None:
            summary["insta_views"] = row["total_v"]
            summary["insta_likes"] = row["total_l"]

        # 최고 조회수 베스트 퍼포머 조회
        cursor.execute("SELECT * FROM posts_metrics ORDER BY views DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            summary["best_performer"] = {
                "platform": row["platform"],
                "title": row["title"],
                "url": row["url"],
                "views": row["views"],
                "likes": row["likes"]
            }
    except Exception as e:
        print(f"⚠️ 마케팅 성과 쿼리 에러: {e}")
    finally:
        conn.close()
    return summary

# 스크립트 단독 호출 시 DB 초기화 실행
if __name__ == "__main__":
    print("📡 [DB 매니저] SQLite 데이터베이스 초기화 진행...")
    init_db()
    log_audit("SYSTEM", "INIT_DB", "SQLite Marketing DB successfully initialized.")
    print(f"✅ DB 초기화 완료: {DB_PATH}")
