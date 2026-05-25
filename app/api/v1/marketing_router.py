from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import json

router = APIRouter()

# 전역 보관용 리스트 (테스트 및 모니터링 시 웹훅 전달 결과 검증용)
received_webhooks = []

class MarketingTriggerInput(BaseModel):
    task_id: str
    product_name: str
    product_description: str

class MarketingTriggerResponse(BaseModel):
    success: bool
    approval_id: str
    message: str
    timestamp: str

class WebhookPayload(BaseModel):
    id: str
    kind: str
    payload: Dict[str, Any]
    approvedAt: str

@router.post("/marketing/trigger", response_model=MarketingTriggerResponse)
async def trigger_marketing_pipeline(data: MarketingTriggerInput):
    """
    개발 완료 이벤트를 수신하여 마케팅 초안 생성 및 텔레그램 승인 플로우를 트리거합니다.
    """
    try:
        # 비즈니스 모듈에서 마케팅 생성 및 승인 요청 생성 호출
        from src.modules.marketing.marketing_module import generate_marketing_package
        
        # 초안 패키지 생성 및 PendingApproval 파일 빌드
        approval_id, message = generate_marketing_package(
            task_id=data.task_id,
            product_name=data.product_name,
            product_description=data.product_description
        )
        
        return MarketingTriggerResponse(
            success=True,
            approval_id=approval_id,
            message=message,
            timestamp=str(time.time())
        )
    except Exception as e:
        print(f"[Marketing Trigger Error] {e}")
        raise HTTPException(
            status_code=500,
            detail=f"마케팅 파이프라인 트리거 실패: {str(e)}"
        )

@router.post("/marketing/webhook")
async def receive_marketing_webhook(payload: WebhookPayload):
    """
    승인(Approved) 시 Node.js 집행자가 최종 콘텐츠를 발송하는 가상 웹훅 게이트웨이 엔드포인트입니다.
    """
    payload_dict = payload.model_dump()
    received_webhooks.append(payload_dict)
    
    return {
        "success": True,
        "message": "웹훅 게이트웨이에 홍보 데이터가 정상 송출되었습니다.",
        "received_count": len(received_webhooks),
        "timestamp": str(time.time())
    }

@router.get("/marketing/webhook/history")
async def get_webhook_history():
    """웹훅 게이트웨이가 수신한 내역 목록을 조회합니다 (유닛 테스트용)."""
    return {
        "count": len(received_webhooks),
        "history": received_webhooks
    }

@router.post("/marketing/webhook/clear")
async def clear_webhook_history():
    """웹훅 수신 내역을 초기화합니다."""
    received_webhooks.clear()
    return {"success": True, "message": "웹훅 내역이 초기화되었습니다."}
