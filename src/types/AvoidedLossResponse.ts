/**
 * @interface AvoidedLossErrorDetail - 개별 필드의 유효성 검사 오류 상세 정보
 * 어떤 변수(field)가 왜 틀렸는지 정확히 알려줍니다.
 */
export interface AvoidedLossErrorDetail {
    field: string;         // 예: "regulatory_risk_score", "data_sovereignty_age"
    received_value: any;   // 사용자가 입력한 값 (디버깅 목적)
    expected_type: 'string' | 'number' | 'boolean'; // 기대하는 데이터 타입
    error_message: string; // 구체적인 오류 메시지
}

/**
 * @interface AvoidedLossErrorPayload - 구조화된 에러 응답 객체 (Failure Case)
 */
export interface AvoidedLossErrorPayload {
    status: 'VALIDATION_ERROR' | 'SYSTEM_ERROR'; // 전체 에러 유형 분류
    code: string;                                  // 내부 고유 오류 코드 (예: E1001, E2005)
    message: string;                               // 사용자에게 보여줄 최상위 메시지
    details?: AvoidedLossErrorDetail[];             // 필드별 상세 검증 오류 목록 (Optional)
    recovery_action: string;                        // 사용자가 취해야 할 조치 (예: "규제 문서를 업로드해주세요.")
}

/**
 * @interface AvoidedLossResponse - 최종 API 응답 계약 (Success OR Failure)
 */
export interface AvoidedLossResponse {
    success: boolean; // 성공 여부 플래그 (가장 먼저 확인)
    data?: {                         // [SUCCESS] 정상적으로 계산된 결과 데이터
        total_avoided_loss: number;   // 총 회피 손실액
        breakdown: Array<{             // 세부 리스크별 기여도 분석
            risk_category: string;
            calculated_loss: number;
            severity_level: 'LOW' | 'MEDIUM' | 'HIGH'; // 신뢰성을 강조하는 요소
            reasoning: string;         // 이 손실이 발생한 논리적 이유 (설득력)
        }>;
        summary_report: string;       // 요약 보고서 텍스트
    } | undefined;

    error_payload?: AvoidedLossErrorPayload; // [FAILURE] 오류 발생 시 상세 페이로드
}