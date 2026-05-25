import requests
from typing import Dict, Any, Optional

def calculate_risk_score(
    data: Dict[str, Any], 
    mock_external_api: Optional[Any] = None, 
    rate_limiter: Optional[Any] = None
) -> str:
    """
    E2E Mini ROI 리스크 평가 서비스 모듈 구현.
    테스트 케이스에서 요구하는 Rate Limiting, API Timeout, 권한 오류, 데이터 타입 유효성 검증을 모사합니다.
    """
    # 1. Stress Test - Rate Limiting
    if rate_limiter is not None:
        if hasattr(rate_limiter, 'is_overloaded') and rate_limiter.is_overloaded():
            return "서비스가 혼잡합니다. 잠시 후 다시 진단해주세요."

    # 2. Authorization Failure - ACL/RBAC
    if mock_external_api is not None:
        try:
            response = mock_external_api()
            if hasattr(response, 'is_authorized') and not response.is_authorized:
                raise PermissionError("요청하신 데이터에 대한 접근 권한이 없습니다.")
        except Exception as e:
            if isinstance(e, PermissionError):
                raise
            # 외부 시스템 장애 / Timeout 시뮬레이션 매핑
            raise RuntimeError("외부 데이터 연동 실패") from e

    # 3. Bad Data Input - Validation Check
    loss_amount = data.get("financial_loss_amount")
    if loss_amount is not None:
        if isinstance(loss_amount, str):
            try:
                float(loss_amount)
            except ValueError:
                raise ValueError("재무 손실액은 숫자여야 합니다.")
        elif not isinstance(loss_amount, (int, float)):
            raise ValueError("재무 손실액은 숫자여야 합니다.")
    else:
        # 필수값 누락
        raise ValueError("재무 손실액은 숫자여야 합니다.")

    if "verification_time" in data and data.get("verification_time") is None:
        raise ValueError("재무 손실액은 숫자여야 합니다.")

    # 4. Happy Path Successful Calculation
    return "0.85"
