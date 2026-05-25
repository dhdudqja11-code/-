#!/usr/bin/env python3
# version: feeder_v1
"""Feedback Feeder — parses the CEO's feedback from Telegram and appends it to the
top-priority joint decisions log decisions.md to enable self-improving RAG behavior.
Also logs audit indicators in SQLite.
"""
import os, sys, time, datetime, subprocess

# Windows 환경 한글 입출력 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
DECISIONS_MD = os.path.join(HERE, "decisions.md")

sys.path.append(HERE)

def feed_feedback(feedback_text):
    """피드백 내용을 decisions.md 공용 파일에 구조적으로 추가 기입하고 SQLite DB에 기록합니다."""
    if not feedback_text or not feedback_text.strip():
        return {"status": "error", "message": "피드백 내용이 비어있습니다."}

    feedback_text = feedback_text.strip()
    current_date = time.strftime('%Y-%m-%d')
    current_time = time.strftime('%Y-%m-%d %H:%M')

    # decisions.md에 포맷 템플릿 구성하여 추가 기입
    entry = f"""

## [{current_date}] [사장님 자율 피드백 피딩] - 실시간 자가 학습 연동
- {feedback_text}
_세션: {current_time}_
"""
    
    try:
        # decisions.md 파일 append 기입
        if os.path.exists(DECISIONS_MD):
            with open(DECISIONS_MD, "a", encoding="utf-8") as f:
                f.write(entry)
        else:
            with open(DECISIONS_MD, "w", encoding="utf-8") as f:
                f.write(f"# 📌 회사 핵심 의사결정 로그 (압축본)\n{entry}")
                
        # SQLite DB 감사 로그 연동 기록
        try:
            import database
            database.init_db()
            database.log_audit("ceo", "FEEDBACK_FEEDED", f"Feedback successfully integrated: {feedback_text}")
        except Exception as e:
            print(f"⚠️ 감사 로그 연동 기록 실패: {e}")

        # RAG 메모리 지능형 다이어트 압축기 백그라운드 트리거 기동 ( Below Normal Priority Class 쿨링 가드 적용 )
        try:
            compressor_py = os.path.join(HERE, "decision_compressor.py")
            win_kwargs = {}
            if sys.platform == "win32":
                win_kwargs["creationflags"] = 0x00004000 # BELOW_NORMAL_PRIORITY_CLASS
            
            # 백그라운드로 안전하게 스폰하여 사장님 대기 시간 0초 보증
            subprocess.Popen([sys.executable, compressor_py], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **win_kwargs)
        except Exception as ex:
            print(f"⚠️ RAG 압축기 트리거 오류: {ex}")

        return {
            "status": "success",
            "timestamp": current_time,
            "feedback": feedback_text,
            "file_path": DECISIONS_MD
        }
    except Exception as e:
        return {"status": "error", "message": f"피드백 반영 처리 도중 파일 쓰기 오류 발생: {e}"}

def main():
    if len(sys.argv) < 2:
        print("❌ 사용법: python feedback_feeder.py \"[피드백 내용]\"")
        sys.exit(1)
        
    feedback_text = sys.argv[1]
    res = feed_feedback(feedback_text)
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
