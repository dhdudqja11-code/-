// src/gateway/types.ts

/**
 * ---------------------------------------------------------------------
 * [PROTOCOL DEFINITION]
 * 모든 통신은 TLS 1.3 기반의 WebSockets을 통해 이루어지며, 메시지는 JSON 페이로드를 사용합니다.
 * 인증 과정에서 JWT 토큰 검증 및 세션 관리가 필수입니다.
 * ---------------------------------------------------------------------
 */

export type RemoteSessionMessage = {
    action: 'AUTH' | 'COMMAND' | 'RESPONSE'; // 행동 유형 정의
    payload: any; // 실제 데이터 로드
    auth_token?: string; // JWT 인증 토큰 (필수)
};

/**
 * ---------------------------------------------------------------------
 * [IMMMUTABLE AUDIT LOG STRUCTURE]
 * 모든 트랜잭션은 이 구조를 따라 기록되어야 하며, 체이닝 해싱을 통해 무결성을 검증합니다.
 * ---------------------------------------------------------------------
 */

export type AuditLogEntry = {
    timestamp: string; // ISO 8601 포맷 (법적 증명 시점)
    transaction_id: string; // 고유 트랜잭션 ID
    source_module: string; // 데이터를 요청한 시스템 모듈 (e.g., 'MiniROISimulator')
    action_taken: string; // 수행된 핵심 액션 (e.g., 'RiskAssessment', 'DataFetch')
    input_data_hash: string; // 입력 데이터의 SHA-256 해시값
    output_result_summary: any; // 결과 요약본 (민감 정보 제외)
    preceding_log_hash: string; // 이전 로그 엔트리의 전체 해시값 (체이닝)
    current_entry_hash: string; // 이 엔트리 자체의 최종 SHA-256 해시값
};

/**
 * ---------------------------------------------------------------------
 * [CORE BUSINESS TYPES]
 * 기존 핵심 비즈니스 로직 타입.
 * ---------------------------------------------------------------------
 */

export type RiskDiagnosis = {
    risk_category: 'Legal' | 'Financial' | 'Compliance'; // 위험 분류
    severity_level: number; // 1 (Low) - 5 (Critical)
    quantitative_loss_estimate: number; // 정량화된 재무 손실 예측액 (KRW)
    mitigation_suggested: string; // 해결책 제시 문구
};

export type GatewayResponse = {
    status: 'SUCCESS' | 'FAILURE';
    message: string;
    data?: any;
}