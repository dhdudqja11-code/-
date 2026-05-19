from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
# 모듈 임포트 시점은 구조가 갖춰진 후 조정됩니다.
from services.purpose_analyzer import PurposeAnalyzerService
from services.risk_data_service import RiskDataService
from services.assurance_calculator import AssuranceCalculatorService

app = FastAPI(title="Assurance Index API Gateway")

# 초기 테스트용 루트 엔드포인트 설정
@app.get("/")
def read_root():
    return {"status": "OK", "message": "Assurance Index API Gateway is running."}

# 실제 구현은 아래 services 디렉토리에 분산됩니다.

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)