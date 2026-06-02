#!/usr/bin/env python3
# version: sessions_gc_v1
"""Sessions Garbage Collector — cleans up empty session directories and archives
older session files into a single zip file to prevent workspace/Git bloating,
while maintaining recent session history for operational continuity.
"""
import os
import sys
import shutil
import zipfile
import re
import time

# Windows console UTF-8 guard
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.abspath(os.path.join(HERE, "..", "sessions"))
ARCHIVE_ZIP_PATH = os.path.join(SESSIONS_DIR, "sessions_history_archive.zip")

# Regex to match session timestamp folder names e.g., 2026-05-16T02-26
SESSION_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}$")

def run_gc(keep_count=30):
    print("🧹 [가비지 컬렉터] 세션 디렉터리 다이어트 시작...")
    
    if not os.path.exists(SESSIONS_DIR):
        print(f"❌ 세션 디렉터리가 존재하지 않습니다: {SESSIONS_DIR}")
        return {"status": "error", "message": "세션 디렉터리 부재"}

    # 1. 모든 하위 디렉터리 스캔
    subdirs = []
    for entry in os.scandir(SESSIONS_DIR):
        if entry.is_dir() and SESSION_PATTERN.match(entry.name):
            subdirs.append(entry)
            
    total_scanned = len(subdirs)
    print(f"📡 총 {total_scanned}개의 세션 폴더 감지됨.")

    # 2. 빈 폴더 즉각 제거 및 비지 않은 폴더 분류
    empty_deleted = 0
    active_sessions = []
    
    for entry in subdirs:
        try:
            files = os.listdir(entry.path)
            if len(files) == 0:
                os.rmdir(entry.path)
                empty_deleted += 1
            else:
                active_sessions.append(entry)
        except Exception as e:
            print(f"⚠️ 폴더 분석 중 오류 ({entry.name}): {e}")
            active_sessions.append(entry)

    print(f"🗑️ 빈 폴더 {empty_deleted}개 즉시 삭제 완료.")
    
    # 3. 비지 않은 세션 폴더 정렬 (이름 순 = 시간 순)
    active_sessions.sort(key=lambda e: e.name)
    total_active = len(active_sessions)
    print(f"📦 실 활성화 세션 폴더: {total_active}개")

    if total_active <= keep_count:
        print(f"✅ 현재 활성 세션({total_active}개)이 유지 기준({keep_count}개) 이하이므로 아카이빙을 건너뜁니다.")
        log_to_db(empty_deleted, 0, 0)
        return {
            "status": "success",
            "empty_deleted": empty_deleted,
            "archived_count": 0,
            "message": "유지 기준 이하로 정리가 생략됨"
        }

    # 4. 아카이브 대상 및 유지 대상 분리
    archive_targets = active_sessions[:-keep_count]
    keep_targets = active_sessions[-keep_count:]
    
    print(f"💾 {len(archive_targets)}개 세션을 아카이브 파일로 이동하고 원본을 삭제합니다.")
    print(f"📌 최신 {len(keep_targets)}개 세션은 원본 보존합니다. (가장 오래된 유지 세션: {keep_targets[0].name})")

    archived_count = 0
    files_archived = 0
    
    # zip 파일 열기 (압축 지원 여부에 따라 예외 처리)
    compression = zipfile.ZIP_DEFLATED
    try:
        # zlib가 없는 비표준 환경 대응용 가드
        import zlib
    except ImportError:
        compression = zipfile.ZIP_STORED
        print("⚠️ zlib 모듈이 없어 압축 없이 zip 아카이브를 진행합니다.")

    try:
        with zipfile.ZipFile(ARCHIVE_ZIP_PATH, mode="a", compression=compression) as archive:
            for entry in archive_targets:
                session_name = entry.name
                folder_path = entry.path
                
                # 폴더 내 모든 파일 압축 저장
                try:
                    for root, _, filenames in os.walk(folder_path):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            # zip 안에서 session_name/filename 구조로 저장
                            arcname = os.path.relpath(file_path, os.path.join(folder_path, ".."))
                            archive.write(file_path, arcname=arcname)
                            files_archived += 1
                    
                    # 압축 성공 시 원본 폴더 삭제
                    shutil.rmtree(folder_path)
                    archived_count += 1
                except Exception as e:
                    print(f"⚠️ 세션 아카이브 실패 ({session_name}): {e}")
                    
    except Exception as e:
        print(f"❌ 아카이브 Zip 파일 열기 실패: {e}")
        return {"status": "error", "message": f"Zip 파일 쓰기 오류: {e}"}

    print(f"✅ {archived_count}개 세션(총 {files_archived}개 파일) 아카이브 완료 및 원본 폴더 삭제.")
    
    # 5. DB 감사 로그 기록
    log_to_db(empty_deleted, archived_count, files_archived)

    return {
        "status": "success",
        "empty_deleted": empty_deleted,
        "archived_count": archived_count,
        "files_archived": files_archived,
        "kept_count": len(keep_targets)
    }

def log_to_db(empty_deleted, archived_count, files_archived):
    try:
        sys.path.append(HERE)
        import database
        database.init_db()
        details = (
            f"Cleared {empty_deleted} empty folders. "
            f"Archived {archived_count} old sessions ({files_archived} files) into Zip. "
            f"Kept the latest 30 sessions in raw folder."
        )
        database.log_audit("SYSTEM", "SESSION_GC_COMPLETED", details)
        print("💾 SQLite 감사 로그 기록 성공.")
    except Exception as e:
        print(f"⚠️ DB 감사 로그 기록 실패: {e}")

if __name__ == "__main__":
    res = run_gc(keep_count=30)
    import json
    print("\n--- 결과 서머리 ---")
    print(json.dumps(res, ensure_ascii=False, indent=2))
