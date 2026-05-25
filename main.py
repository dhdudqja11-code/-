import uvicorn
from fastapi import FastAPI, Request, status
from typing import Dict, Any

# 🚨 핵심 모듈 임포트 (절대 경로 준수)
from src.middleware.auth import get_auth_middleware
from src.gateway.compliance_gateway import ComplianceGateway, ComplianceGatewayError
from src.logging.audit_logger import AuditLoggerService

app = FastAPI(title="Compliance-First API Gateway")

# ---------------------------
# 1. Middleware 적용 (가장 먼저 실행됨)
# 요청이 오면 무조건 인증을 시도합니다.
app.add_middleware(get_auth_middleware())


@app.post("/api/v1/process_data", status_code=status.HTTP_200_OK)
async def process_user_data(request: Request, data: dict):
    """
    사용자가 데이터를 전송하여 처리하는 핵심 엔드포인트입니다. 
    요청 흐름: Middleware -> Gateway Check -> Core Logic -> Logging
    """
    # 요청 객체에서 사용자 ID를 안전하게 가져옵니다. (Middleware가 성공적으로 실행되었음을 가정)
    try:
        user_id = request.state.user_id
    except AttributeError:
        # 미들웨어가 실패하면 이미 401 에러로 처리되므로 이 부분은 이론상 도달하지 않음
        return {"error": "User context unavailable."}


    # 2. 컴플라이언스 게이트웨이 강제 실행 (가장 중요)
    try:
        audit_result = ComplianceGateway.execute(
            user_id=user_id, 
            request_data=data, 
            endpoint_name="process_user_data"
        )

    except ComplianceGatewayError as e:
        # 규정 위반 시 시스템 다운 방지 및 명확한 오류 반환 (Cost Avoidance 관점)
        print(f"[🚨 COMPLIANCE FAILURE] {e}")
        return {
            "status": "REJECTED", 
            "error_code": "COMPLIANCE_VIOLATION",
            "details": {
                "what": e.what,
                "why": e.why,
                "how_to_fix": e.how
            }
        }

    # 3. 핵심 비즈니스 로직 실행 (Gateway를 통과한 데이터만 처리)
    print("\n[✅ CORE LOGIC] Compliance Gate passed. Executing core business logic...")
    
    # 가상의 핵심 프로세스 수행 (예: Mini ROI 계산, DB 업데이트 등)
    result = f"Successfully processed data for {user_id}. Risk Score calculated and Mitigation Plan applied."

    # 4. 최종 감사 기록 반환
    return {
        "status": "SUCCESS",
        "message": result,
        "audit_record": audit_result # 게이트웨이에서 생성된 증거 기록을 클라이언트에 노출
    }


if __name__ == "__main__":
    # 테스트 실행 시 주의: 환경 변수와 실제 라이브러리 설치가 필요합니다.
    print("=============================================")
    print("🚀 API Gateway Skeleton Initialized.")
    print("엔드포인트: POST /api/v1/process_data")
    print("요청 헤더 필수값: Authorization: Bearer <TOKEN>")
    print("=============================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)