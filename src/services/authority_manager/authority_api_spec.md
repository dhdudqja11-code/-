# Authority Manager API Specification (v1.0)

## Overview
This service calculates the 'Authority Score' based on compliance gaps identified by $L_{reg}$ data and simulates the mandatory state transition process (IDLE $\to$ WARNING $\to$ AUTHORITY). It acts as the core logic engine for proving systemic control, not just regulatory adherence.

## Endpoint: POST /api/v1/authority/check_score
**Purpose:** Receive transaction context and $L_{reg}$ data to calculate Authority Score and determine current system state.

### Request Body (JSON Schema)
```json
{
  "transaction_id": "string",           // Unique ID of the assessed transaction.
  "timestamp": "ISO 8601 date string", // Time of transaction occurrence.
  "source_system": "string",            // Originating system/module (e.g., 'PaymentGateway', 'DataPipeline').
  "input_data": {                       // The raw data payload being assessed.
    "user_id": "string",
    "transaction_amount": "number",
    "regulatory_fields": [              // Specific fields needing compliance check (e.g., 'KYC', 'SourceIP').
      {"field_name": "string", "value": "string"},
      // ... more fields
    ]
  },
  "l_reg_data": {                       // Pre-fetched regulatory data set for comparison.
    "region": "string",                 // e.g., 'EU', 'US', 'KR'
    "applicable_rules": [               // List of relevant regulations/rules.
      {"rule_id": "string", "severity": "HIGH|MEDIUM|LOW"} 
      // Severity is derived from the L_reg dataset analysis.
    ]
  }
}
```

### Response Body (JSON Schema)
```json
{
  "status": "string",                    // System State: IDLE, WARNING, AUTHORITY
  "authority_score": "number",          // Calculated score (0 to 100). Lower is riskier.
  "assessment_details": {                // Structured output for debugging and display.
    "risk_level": "string",              // Overall categorized risk ('LOW', 'MEDIUM', 'HIGH').
    "compliance_gaps": [                 // List of identified compliance gaps.
      {
        "field_name": "string",
        "required_rule_id": "string",
        "gap_description": "string",     // What is missing or incorrect?
        "mitigation_advice": "string"    // The immediate solution required (Actionable).
      }
    ],
    "state_transition_justification": "string" // Why did the state transition to its current status?
  },
  "authority_warning": {                // Mandatory structure for non-IDLE states.
    "alert_type": "string",              // e.g., 'Data Integrity Alert', 'Jurisdictional Risk'
    "what_went_wrong": "string",        // [1] Problem Definition (Visible to User)
    "reason_analysis": "string",        // [2] Root Cause Analysis (Technical/Expert View)
    "mitigation_steps": ["string"]      // [3] Actionable Solution Steps (The 'Authority' steps)
  }
}
```

### State Transition Logic Mapping
*   **IDLE $\to$ WARNING:** Occurs when `compliance_gaps` are found, but the gap is fixable with clear advice. Score drops below a defined threshold (e.g., < 85).
*   **WARNING $\to$ AUTHORITY:** Requires successful completion of all steps listed in `mitigation_steps`. The system must prove *control*. Score increases to the high range (> 95).