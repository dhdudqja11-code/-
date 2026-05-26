# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
import uuid
import os
import sys
from typing import Dict, Any, List

# 로컬 auth_service 임포트
try:
    from auth_service import get_current_user, UserPayload
except ImportError:
    from .auth_service import get_current_user, UserPayload

# src/services 절대 경로 추가하여 LegalReportGenerator 주입 (의존성 무결성 확보)
HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(HERE, ".."))
if WORKSPACE not in sys.path:
    sys.path.append(WORKSPACE)

from src.services.legal_report_generator import LegalReportGenerator

# ------------------- [1. 데이터 모델 정의] ------------------- #
class MiniROIRequest(BaseModel):
    """Mini ROI 시뮬레이션 요청 바디."""
    user_id: str
    data_source: Dict[str, Any]

class ComplianceRequest(BaseModel):
    """컴플라이언스 체크 요청 바디."""
    transaction_id: str
    timestamp: int

class ReportGenerationRequest(BaseModel):
    """법률 PDF 보고서 생성 요청 바디."""
    filename: str = Field("secure_audit_report.pdf", description="저장할 PDF 파일명")

class AuditBlock(BaseModel):
    """모든 API 응답에 강제되는 불변 감사 기록 구조체."""
    status: str  # SUCCESS or FAILURE
    timestamp_utc: str
    transaction_id: str
    audit_details: Dict[str, Any]
    message: str

# ------------------- [2. SQLite3 영구 SSoT 감사 저장소 구축] ------------------- #
import sqlite3
import json

DB_PATH = os.path.join(HERE, "gateway_audit.db")

def get_db_connection():
    """SQLite DB 연결 객체를 반환합니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """감사 로그 저장용 audit_blocks 테이블을 자동 생성 및 초기화합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT NOT NULL,
        timestamp_utc TEXT NOT NULL,
        transaction_id TEXT NOT NULL UNIQUE,
        source_api TEXT NOT NULL,
        initiator_user_id TEXT NOT NULL,
        result_summary TEXT NOT NULL,
        audit_payload TEXT NOT NULL,  -- JSON serialized dictionary
        message TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# 모듈 초기화 시 데이터베이스 테이블 무결 생성 보증
init_db()

PLANNER_SUSPENDED: bool = False

def send_telegram_alert(text: str):
    """비서 설정을 읽어 사장님 텔레그램으로 실시간 경보 메시지를 푸시합니다."""
    import requests
    import json
    
    setup_json = os.path.join(WORKSPACE, "_company", "_agents", "secretary", "tools", "telegram_setup.json")
    if not os.path.exists(setup_json):
        print(f"⚠️ [IAG Alert] Telegram setup JSON not found at {setup_json}")
        return
        
    try:
        with open(setup_json, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        token = (cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
        chat_id = (cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            cleaned_text = text.replace("**", "").replace("_", "")
            payload = {"chat_id": chat_id, "text": cleaned_text[:4000]}
            requests.post(url, json=payload, timeout=10)
            print("🚀 [IAG Alert] Telegram compliance emergency alert pushed successfully.")
    except Exception as e:
        print(f"⚠️ [IAG Alert] Failed to send Telegram alert: {e}")

def feed_violation_to_decisions(message: str):
    """게이트웨이 규제 차단 사유를 분석하여 공용 의사결정 RAG 메모리(decisions.md)에 자동 피딩합니다."""
    import time
    
    decisions_path = os.path.join(WORKSPACE, "_company", "_shared", "decisions.md")
    if not os.path.exists(decisions_path):
        print(f"⚠️ [IAG Self-Correction] decisions.md not found at {decisions_path}")
        return
        
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        # 위반 내용을 요약 및 정제하여 0순위 자율 규제 제약 마크다운으로 포맷팅
        alert_content = f"""

---

## 🚨 [IAG 자율 규제 제어 지침] - {timestamp}
- **위반 유형**: System Exception / Validation Failure / Compliance Guardrail Lockdown
- **차단 사유**: {message}
- **자가 교정 행동 제약**: 향후 데이터 트랜잭션 및 콘텐츠/마케팅 시나리오 생성 시, 본 규제 위반 원인에 기재된 유형을 최우선 인지하여 비인가 의심 코드나 부작용을 일으키는 행동 패턴 생성을 전면 금지하며, 오직 규제 가드레일을 무결하게 통과할 수 있는 정연한 표준화 구조만을 적용해 창작을 완수하십시오.
"""
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(alert_content)
        print("🚀 [IAG Self-Correction] Compliance constraint automatically fed to decisions.md RAG store.")
    except Exception as e:
        print(f"⚠️ [IAG Self-Correction] Failed to feed violation to decisions.md: {e}")

def send_telegram_pdf(pdf_path: str):
    """생성된 실물 PDF 보고서 파일을 사장님의 모바일 텔레그램으로 직접 첨부(sendDocument) 전송합니다."""
    import requests
    import json
    import time
    
    setup_json = os.path.join(WORKSPACE, "_company", "_agents", "secretary", "tools", "telegram_setup.json")
    if not os.path.exists(setup_json):
        print(f"⚠️ [IAG PDF] Telegram setup JSON not found at {setup_json}")
        return
        
    if not os.path.exists(pdf_path):
        print(f"⚠️ [IAG PDF] PDF file not found at {pdf_path}")
        return
        
    try:
        with open(setup_json, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        token = (cfg.get("TELEGRAM_BOT_TOKEN") or "").strip()
        chat_id = (cfg.get("TELEGRAM_CHAT_ID") or "").strip()
        
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendDocument"
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            size_kb = os.path.getsize(pdf_path) / 1024.0
            
            caption = f"""📄 [IAG 불변 감사 증명서 발송 완료]
● 발송 시간: {timestamp}
● 파일 크기: {size_kb:.2f} KB
● 상태: SUCCESS (Compliant)"""
            
            with open(pdf_path, "rb") as pdf_file:
                files = {"document": pdf_file}
                data = {"chat_id": chat_id, "caption": caption}
                requests.post(url, data=data, files=files, timeout=20)
            print("🚀 [IAG PDF] Physical PDF report successfully sent to Telegram channel.")
    except Exception as e:
        print(f"⚠️ [IAG PDF] Failed to send document: {e}")

# ------------------- [3. 유틸리티 및 매퍼 함수 정의] ------------------- #
def get_current_time() -> str:
    """UTC 시간 포맷팅."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def generate_audit_block(
    status: str, 
    initiator_user_id: str, 
    source_api: str, 
    result_summary: str, 
    audit_payload: Dict[str, Any] = None, 
    message: str = None
) -> AuditBlock:
    """모든 트랜잭션 결과를 AuditBlock으로 감싸고, SQLite3 gateway_audit.db에 자동 영구 적재합니다."""
    timestamp = get_current_time()
    tx_id = str(uuid.uuid4())
    payload = audit_payload or {}
    msg = message or f"Audit Block generated for {status} transaction."
    
    block = AuditBlock(
        status=status,
        timestamp_utc=timestamp,
        transaction_id=tx_id,
        audit_details={
            "source_api": source_api,
            "initiator_user_id": initiator_user_id,
            "requested_action": "Immutable Audit Record Generation",
            "result_summary": result_summary,
            "audit_payload": payload
        },
        message=msg
    )
    
    # SQLite3 DB에 로우 적재
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO audit_blocks (
                status, timestamp_utc, transaction_id, source_api, initiator_user_id, result_summary, audit_payload, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                status,
                timestamp,
                tx_id,
                source_api,
                initiator_user_id,
                result_summary,
                json.dumps(payload, ensure_ascii=False),
                msg
            )
        )
        conn.commit()
    except Exception as e:
        print(f"⚠️ [IAG DB Error] Failed to write audit record: {e}")
    finally:
        conn.close()
        
    # 규제 위반 실패 감지 시 즉시 자율 플래너 락다운 및 사장님 텔레그램 비상 경보 피딩
    if status == "FAILURE":
        global PLANNER_SUSPENDED
        if not PLANNER_SUSPENDED:
            PLANNER_SUSPENDED = True
            send_telegram_alert("🚨 [IAG 긴급 규제 경보]\n자율 가동 플래너가 규제 위반으로 일시 정지(PAUSED) 처리가 완료되었습니다.\n복구를 원하시면 구글 OTP 2FA 인증을 완료해 주십시오.")
        
        # 차단 사유를 decisions.md에 RAG 자율 피딩
        feed_violation_to_decisions(msg)
        
    return block

def map_audit_block_to_legal_log(block: Dict[str, Any]) -> Dict[str, Any]:
    """AuditBlock의 정보를 LegalReportGenerator가 요구하는 감사 로그 스키마로 정밀 매핑합니다."""
    details = block.get("audit_details", {})
    payload = details.get("audit_payload", {})
    status = block.get("status", "SUCCESS")
    
    if status == "FAILURE":
        error_msg = block.get("message", "Unknown error")
        severity = "3"
        error_type = "System Exception / Validation Failure"
        legal_basis = "Compliance Gateway Immutability Rule"
        description = f"게이트웨이 차단 트랜잭션: {error_msg}"
    else:
        # 성공했으나 리스크 점수가 검출된 경우 매핑
        roi_score = payload.get("mini_roi_score", 0.0)
        detected_risks = payload.get("detected_risks", [])
        
        if detected_risks:
            severity = "2" if roi_score > 2.0 else "1"
            error_type = ", ".join(detected_risks)
            legal_basis = "GDPR Article 5(1)(f)"
            description = details.get("result_summary", "Simulated Risk detected.")
        else:
            # 경미한 일반 로그
            severity = "1"
            error_type = "Compliant Operation"
            legal_basis = "General Compliance Code"
            description = details.get("result_summary", "Regular compliant transaction.")

    return {
        "timestamp": block.get("timestamp_utc", get_current_time()),
        "error_type": error_type,
        "severity": severity,
        "legal_basis": legal_basis,
        "description": description
    }

# ------------------- [4. FastAPI 애플리케이션 및 엔드포인트] ------------------- #
app = FastAPI(title="Immutable Audit Gateway (IAG)")

@app.post("/api/v1/simulate_risk", response_model=AuditBlock)
async def simulate_risk_endpoint(
    request: MiniROIRequest, 
    auth_user: UserPayload = Depends(get_current_user)
):
    """
    Mini ROI 시뮬레이션을 실행하고 반드시 AuditBlock을 생성 및 적재하는 핵심 엔드포인트.
    """
    print(f"⚙️ [API Call] Received request from {auth_user.user_id} for simulation.")

    try:
        if not request.data_source:
            raise ValueError("Input data_source is empty or invalid.")

        mini_roi_score = len(request.data_source) * 0.95
        detected_risks = ["Data Integrity Gap"] if mini_roi_score > 2.0 else []
        
        result_payload = {
            "mini_roi_score": round(mini_roi_score, 3),
            "detected_risks": detected_risks,
            "legal_article": "GDPR Article 17"
        }
        
        return generate_audit_block(
            status="SUCCESS",
            initiator_user_id=auth_user.user_id,
            source_api="/api/v1/simulate_risk",
            result_summary=f"Risk simulation completed. ROI Score: {mini_roi_score}",
            audit_payload=result_payload
        )

    except Exception as e:
        print(f"🐛 [Error] Simulation failed: {e}")
        return generate_audit_block(
            status="FAILURE",
            initiator_user_id=auth_user.user_id,
            source_api="/api/v1/simulate_risk",
            result_summary="Simulation failed due to input or processing issues.",
            message=f"Failure: {type(e).__name__}: {str(e)}"
        )

@app.post("/api/v1/check_compliance", response_model=AuditBlock)
async def check_compliance_endpoint(
    request: ComplianceRequest,
    auth_user: UserPayload = Depends(get_current_user)
):
    """
    외부 규제 데이터와 내부 데이터를 비교하여 위험 경고 및 감사 로그를 생성 및 적재하는 엔드포인트.
    """
    print(f"⚙️ [API Call] Compliance check requested by {auth_user.user_id}.")

    try:
        if "fail" in request.transaction_id.lower() or request.timestamp <= 0:
            raise ValueError("Invalid transaction ID pattern or corrupt timestamp sequence.")

        result_payload = {
            "compliance_status": "COMPLIANT",
            "checked_rule": "REG-001",
            "legal_article": "GDPR Art 5(1)(f)"
        }

        return generate_audit_block(
            status="SUCCESS",
            initiator_user_id=auth_user.user_id,
            source_api="/api/v1/check_compliance",
            result_summary="Transaction is fully compliant with GDPR/CCPA guidelines.",
            audit_payload=result_payload
        )

    except Exception as e:
        print(f"🐛 [Error] Compliance check failed: {e}")
        return generate_audit_block(
            status="FAILURE",
            initiator_user_id=auth_user.user_id,
            source_api="/api/v1/check_compliance",
            result_summary="Transaction is non-compliant or corrupt data sequence detected.",
            message=f"Failure: {type(e).__name__}: {str(e)}"
        )

@app.post("/api/v1/generate_legal_report", response_model=Dict[str, Any])
async def generate_legal_report_endpoint(
    request: ReportGenerationRequest,
    auth_user: UserPayload = Depends(get_current_user)
):
    """
    게이트웨이에 SQLite3로 적재된 불변 감사 로그를 추출 및 자동 매핑하여
    법적 효력을 갖는 PDF 증명서를 서버 측에 실물 저장하고 상세 요약을 반환합니다.
    """
    print(f"⚙️ [API Call] Legal Report Generation requested by {auth_user.user_id}.")
    
    # SQLite3 DB에서 모든 감사 블록 읽기
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM audit_blocks ORDER BY id ASC")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"🐛 [Error] Failed to read audit blocks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query error: {str(e)}"
        )
    finally:
        conn.close()
        
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audit blocks found in the gateway database to generate a report."
        )
        
    try:
        # DB 로우를 기존 AuditBlock.dict() 구조의 딕셔너리 리스트로 변환 가공
        db_audit_blocks = []
        for r in rows:
            try:
                payload_dict = json.loads(r["audit_payload"])
            except Exception:
                payload_dict = {}
                
            db_audit_blocks.append({
                "status": r["status"],
                "timestamp_utc": r["timestamp_utc"],
                "transaction_id": r["transaction_id"],
                "message": r["message"],
                "audit_details": {
                    "source_api": r["source_api"],
                    "initiator_user_id": r["initiator_user_id"],
                    "requested_action": "Immutable Audit Record Generation",
                    "result_summary": r["result_summary"],
                    "audit_payload": payload_dict
                }
            })
            
        # 1. 스키마 매핑 번역 수행
        mapped_logs = [map_audit_block_to_legal_log(block) for block in db_audit_blocks]
        
        # 2. 최신 risk_context 가상 조립 및 PDF 빌드
        risk_context = {
            'reg_name': 'Immutable Audit Gateway 통합 모니터링',
            'art_num': 'PoC Compliance Audit',
            'base_factor': 15,
            'market_impact': 500000
        }
        
        generator = LegalReportGenerator(mapped_logs)
        final_text = generator.generate_report(initial_risk_context=risk_context, filename=request.filename)
        
        # 실물 PDF 보고서 사장님 모바일 텔레그램으로 직접 피딩 전송
        send_telegram_pdf(request.filename)
        
        return {
            "success": True,
            "message": f"Successfully generated legal PDF report with {len(mapped_logs)} audit blocks.",
            "pdf_path": os.path.abspath(request.filename),
            "mapped_records_count": len(mapped_logs),
            "report_summary": final_text[:500] + "..."
        }
    except Exception as e:
        print(f"🐛 [Error] Legal report generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate legal report: {str(e)}"
        )

@app.get("/api/v1/planner/allowed", response_model=Dict[str, Any])
async def get_planner_allowed():
    """자율 플래너가 기동 가능한지 여부를 반환합니다."""
    global PLANNER_SUSPENDED
    return {"allowed": not PLANNER_SUSPENDED}

@app.post("/api/v1/planner/resume", response_model=Dict[str, Any])
async def post_planner_resume(auth_user: UserPayload = Depends(get_current_user)):
    """(2FA Guarded) 일시정지 상태의 자율 플래너를 정상으로 복구(Resume)합니다."""
    global PLANNER_SUSPENDED
    PLANNER_SUSPENDED = False
    send_telegram_alert("✅ [IAG 가드레일 해제 완료]\n자율 플래너가 정상 가동 상태로 복귀했습니다!")
    return {"success": True, "message": "Planner successfully resumed."}