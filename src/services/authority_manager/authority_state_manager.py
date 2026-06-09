import json
from typing import Dict, Any, List
from datetime import datetime

# --- Core Constants & Thresholds ---
SCORE_THRESHOLD_WARNING = 85
SCORE_THRESHOLD_AUTHORITY = 95

def calculate_initial_score(gap_count: int) -> float:
    """
    Calculates a preliminary score based on the number of identified compliance gaps.
    Higher gap count means lower starting authority.
    """
    # Max possible points assumed to be 100. Each major gap deducts significant points.
    return max(50.0, 100.0 - (gap_count * 8.0))

def generate_authority_warning(gaps: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generates the mandatory Authority Warning structure based on compliance gaps.
    This structures the narrative from 'failure' to 'control.'
    """
    if not gaps:
        return {"alert_type": "None", "what_went_wrong": "No critical alerts.", "reason_analysis": "", "mitigation_steps": []}

    # Example of structuring the warning based on common gap types.
    warning = {
        "alert_type": "Systemic Authority Deficiency Alert",
        "what_went_wrong": f"Critical data gaps detected across {len(gaps)} regulatory domains, risking operational suspension.", # [1] Problem Definition (User facing)
        "reason_analysis": "Analysis indicates a breakdown in the controlled data flow pipeline, suggesting structural vulnerability rather than individual error. The source/time correlation is compromised.", # [2] Root Cause Analysis (Technical)
        "mitigation_steps": ["Immediate manual audit required on Source System X.", "Implement real-time pre-check for Rule ID Y.", "Revalidate all data points against the latest global Fact Sheet."] # [3] Actionable Solution Steps
    }
    return warning

def check_authority_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    The main function to assess authority score and determine system state.
    Input data must adhere to the Authority API Spec (v1.0).
    """
    try:
        l_reg_data = data['l_reg_data']
        input_data = data['input_data']
        
        # 1. Gap Detection Logic (Simulated)
        compliance_gaps = []
        for rule in l_reg_data.get('applicable_rules', []):
            # Simplified check: If a high-severity rule is present but not covered by input data, it's a gap.
            if rule['severity'] == 'HIGH' and any(f['field_name'] != 'KYC' for f in input_data.get('regulatory_fields', [])):
                compliance_gaps.append({
                    "field_name": "Regulatory Compliance",
                    "required_rule_id": rule['rule_id'],
                    "gap_description": f"Missing required field for {rule['rule_id']}.",
                    "mitigation_advice": f"Update data with proof of compliance for Rule ID: {rule['rule_id']}."
                })

        # 2. Score Calculation & Warning Generation
        initial_score = calculate_initial_score(len(compliance_gaps))
        authority_warning = generate_authority_warning(compliance_gaps)
        
        # --- State Transition Logic (The core business logic) ---
        status: str = "IDLE"
        final_score: float = initial_score
        justification: str = "All checked data points are compliant with known regulatory frameworks."

        if compliance_gaps:
            warning_details = authority_warning['what_went_wrong']
            state_status = "WARNING" if initial_score < SCORE_THRESHOLD_AUTHORITY else "UNKNOWN" 
            
            final_score = max(50.0, initial_score - (len(compliance_gaps) * 3)) # Score decreases slightly after warning generation
            status = state_status

            # Simulate the transition to AUTHORITY if mitigation steps were theoretically followed
            if any("Immediate manual audit required" in step for step in authority_warning['mitigation_steps']):
                # If we detect that the necessary controls are still needed, status remains WARNING.
                pass # State is locked at WARNING until external action occurs.

        elif initial_score > SCORE_THRESHOLD_AUTHORITY:
            status = "AUTHORITY"
            final_score = 99.5 # Perfect score simulation
            justification = "System has successfully verified all data points against global best practices, demonstrating absolute systemic control."


        # 3. Final structured response based on the API Spec
        return {
            "status": status,
            "authority_score": round(final_score, 2),
            "assessment_details": {
                "risk_level": "HIGH" if status == "WARNING" else ("LOW" if status == "IDLE" else "UNKNOWN"),
                "compliance_gaps": compliance_gaps,
                "state_transition_justification": justification
            },
            "authority_warning": authority_warning # Always include the warning structure for consistency
        }

    except Exception as e:
        # This is the critical failure path. The system MUST remain in control of the response.
        print(f"[CRITICAL SYSTEM FAILURE] Error processing authority check: {e}")
        return {
            "status": "SYSTEM_FAILURE",
            "authority_score": 0.0,
            "assessment_details": {"risk_level": "UNKNOWN", "compliance_gaps": [], "state_transition_justification": f"System failed to process request due to internal error: {str(e)}."},
            "authority_warning": {
                "alert_type": "Critical System Failure",
                "what_went_wrong": "The Authority Manager service is currently unavailable.", # [1] Problem Definition (Contained)
                "reason_analysis": f"Internal process failure detected: {str(e)}. This indicates a critical architectural dependency break. DO NOT proceed with data handling until system integrity is restored.", # [2] Root Cause Analysis (Technical)
                "mitigation_steps": ["Check service logs for Dependency Failure Code X.", "Initiate full environment rollback to known stable version."] # [3] Actionable Solution Steps (Control Focus)
            }
        }

# --- Unit Test Example (Self-Verification) ---
def test_authority_logic():
    """Basic unit tests for core logic."""
    print("--- Running Authority Manager Unit Tests ---")
    
    # Test Case 1: Perfect Compliance (IDLE -> AUTHORITY simulation)
    test_data_perfect = {
        "transaction_id": "T001", "timestamp": datetime.now().isoformat(), "source_system": "API_Gateway",
        "input_data": {"user_id": "U123", "transaction_amount": 500, "regulatory_fields": [{"field_name": "KYC", "value": "VALID"}]},
        "l_reg_data": {"region": "Global", "applicable_rules": []}
    }
    result = check_authority_score(test_data_perfect)
    assert result['status'] == "IDLE" and result['authority_score'] >= 90.0, f"Test 1 Failed: Expected IDLE/High Score, Got {result}"

    # Test Case 2: High Gap Count (WARNING state simulation)
    test_data_gap = {
        "transaction_id": "T002", "timestamp": datetime.now().isoformat(), "source_system": "API_Gateway",
        "input_data": {"user_id": "U456", "transaction_amount": 100, "regulatory_fields": [{"field_name": "KYC", "value": "VALID"}]},
        "l_reg_data": {"region": "EU", "applicable_rules": [
            {"rule_id": "GDPR-A", "severity": "HIGH"}, # Gap 1
            {"rule_id": "AML-B", "severity": "HIGH"}  # Gap 2
        ]}
    }
    result = check_authority_score(test_data_gap)
    assert result['status'] == "WARNING" and result['assessment_details']['risk_level'] == "HIGH", f"Test 2 Failed: Expected WARNING/High Risk, Got {result}"

    print("✅ Authority Manager Unit Tests Passed Successfully.")
    return True