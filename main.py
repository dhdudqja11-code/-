from fastapi import FastAPI
from app.api.v1 import avoided_loss_router

# 앱 초기화
app = FastAPI(title="사업 기획소 - Avoided Loss API Gateway")

# 라우터 포함
app.include_router(avoided_loss_router.router, prefix="/api/v1", tags=["AvoidedLoss"])


@app.get("/")
def read_root():
    return {"message": "사업 기획소 - Avoided Loss API Gateway is running."}

# 참고: 실제 실행은 'uvicorn main:app --reload' 명령으로 합니다.