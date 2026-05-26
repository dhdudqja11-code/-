/**
 * @fileoverview Immutable Audit Log 시스템에서 사용되는 공통 타입 정의 파일.
 * 모든 트랜잭션 데이터, 성공/실패 여부, 그리고 분석 결과를 표준화합니다.
 */

// API 요청에 들어오는 모든 원본 Payload의 형태를 정의
export type IncomingPayload = {
    source: string;       // 호출 주체 (e.g., 'web-client', 'webhook-partner')
    user_id?: string | null; // 사용자 식별자
    data: Record<string, any>; // 실제 분석에 필요한 데이터 묶음
};

// 트랜잭션의 최종 결과 구조를 정의합니다. (3단계 논리 구조 강제)
export type AnalysisResult = {
    status: 'SUCCESS' | 'FAILURE'; // 성공 또는 실패
    timestamp_utc: string;        // UTC 시간 기록
    problem_definition: string;   // [1] 문제 정의 (What went wrong?)
    cause_analysis: string;       // [2] 원인 분석 (Why did it go wrong? Source/Time)
    mitigation_suggestion: string;// [3] 해결책 제시 (How to fix it?)
    raw_data: Record<string, any>; // 원본 데이터 참조를 위한 필드
}

// 감사 로그에 기록될 최종 구조체
export type AuditLogEntry = {
    log_id: string;       // 고유 트랜잭션 ID (UUID)
    timestamp: string;    // 로그 기록 시간
    status: 'SUCCESS' | 'FAILURE'; // 결과 상태
    input_payload: IncomingPayload;
    output_result: AnalysisResult;
    is_immutable: boolean; // 이 필드는 항상 true여야 함
};

export type GatewayResponse = {
    success: boolean;
    message: string;
    data: any;
}