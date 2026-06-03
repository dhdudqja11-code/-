import json
from typing import Dict, Any, List

# 프로젝트 내부에 존재하는 규제 위반 사례 데이터를 로드하는 함수
def load_violation_data(file_path: str) -> List[Dict[str, Any]]:
    """규제 위반 사례 JSON 파일을 읽고 리스트 형태로 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] 규제 위반 데이터 파일이 없습니다.")
        return []
    except json.JSONDecodeError:
        print("[ERROR] JSON 디코딩 오류가 발생했습니다. 파일 형식을 확인하세요.")
        return []

def generate_authority_warning(violation_data: List[Dict[str, Any]], case_id: str = None) -> Dict[str, str]:
    """
    주어진 규제 위반 데이터를 기반으로 시스템이 통제권을 회복하며 출력할 '권위적 경고' 메시지를 생성합니다.

    Args:
        violation_data: load_violation_data로 불러온 규제 위반 사례 리스트.
        case_id: 특정 케이스를 지정할 때 사용되는 ID (선택 사항).

    Returns:
        권위적 경고 메시지 딕셔너리.
    """
    if not violation_data:
        return {"status": "FATAL", "message": "데이터 로드 실패: 권위적 경고를 생성할 근거 데이터가 없습니다.", "details": ""}

    selected_case = None
    if case_id:
        # 특정 ID로 검색하여 케이스 선택 (권장 방식)
        for item in violation_data:
            if item.get("id") == case_id:
                selected_case = item
                break
    else:
        # 가장 첫 번째 사례를 기본으로 사용하거나, 최신/가장 심각한 것으로 로직화할 수 있음.
        selected_case = violation_data[0]

    if not selected_case:
        return {"status": "FAILURE", "message": "처리 실패: 지정된 규제 위반 사례를 찾을 수 없습니다.", "details": ""}

    # --- 핵심 권위적 경고 메시지 포맷팅 로직 시작 ---
    warning = {
        "status": "WARNING_AUTHORITY_RECOVERY",
        "title": f"[🚨 시스템 권위 경고: 규제 위반 감지 ({selected_case['id']})] - {selected_case['Regulation Name']} 관련.",
        "message": (
            f"⚠️ **[경고]** 현재 분석 과정에서 치명적인 법률 리스크가 감지되었습니다. "
            f"이는 단순한 오류가 아니며, 시스템의 즉각적인 통제권 재확보를 요구합니다."
        ),
        "details": f"""
- **규정:** {selected_case['Regulation Name']}
- **위반 메커니즘:** {selected_case['Violation Mechanism']}
- **핵심 조항 근거:** `{selected_case['Core Article']}`
- **재무적 영향 (Financial Impact):** {selected_case['Financial_Impact']}에 달하는 막대한 리스크가 잠재되어 있습니다.
"""
    }
    # --- 핵심 권위적 경고 메시지 포맷팅 로직 끝 ---
    return warning


class AuthorityChecker:
    """원격지 제어의 권위 복구 흐름을 진단하고 확인하는 통합 검증 체커 클래스"""
    
    def __init__(self, system_id: str):
        self.system_id = system_id

    def run_remote_check(self, payload: Dict[str, Any]) -> str:
        """외부 위험 상태 값을 입력받아 JSON 파싱 및 권위 경고 출력 플로우를 가동합니다."""
        external_risk_payload = payload.get('external_risk_payload')
        if not external_risk_payload:
            return "structural integrity failure: missing external_risk_payload"
        
        try:
            data = json.loads(external_risk_payload)
        except Exception:
            return "structural integrity failure: failed to parse JSON"
            
        is_violating = data.get("is_violating", False)
        if is_violating:
            violation_type = data.get("violation_type", "Unknown")
            legal_article = data.get("legal_article", "N/A")
            return f"SYSTEM AUTHORITY ALERT: {violation_type} detected. Violating {legal_article}."
        else:
            return "Status OK: No violations detected."


if __name__ == '__main__':
    # 테스트 실행 예시: 데이터/regulatory_violation_schema.json 경로를 가정
    test_data_path = "data/regulatory_violation_schema.json" 
    print(f"--- 로딩 중: {test_data_path} ---")
    all_cases = load_violation_data(test_data_path)
    
    if all_cases:
        # 첫 번째 사례를 이용한 경고 생성 테스트
        first_case_id = all_cases[0]['id']
        warning_msg = generate_authority_warning(all_cases, case_id=first_case_id)

        print("\n=============================================================")
        print("🔑 [시스템 테스트 실행] 권위적 경고 메시지 시뮬레이션 출력")
        print("=============================================================\n")
        print(f"상태: {warning_msg['status']}")
        print(f"제목: {warning_msg['title']}")
        print("-------------------------------------------------------------")
        # 실제 UI에 표시될 형식으로 포맷팅하여 출력합니다.
        print(f"{warning_msg['message']}\n{warning_msg['details'].strip()}")
        print("\n=============================================================")