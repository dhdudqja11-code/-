/**
 * Authority Meter 상태 관리를 위한 전역 타입을 정의합니다.
 */

export type AuthorityState = 'IDLE' | 'ANALYZING' | 'WARNING' | 'CONTROLLED';

/**
 * L_reg 데이터셋 스키마 (Researcher가 확정한 구조)를 기반으로 확장된 타입입니다.
 */
export interface LRegData {
    authorityScore: number; // 0.0 ~ 100.0
    lRegEstimateUsd: number; // 최소 예상 벌금액 (핵심 트igger 값)
    violationCount: number; // 위반 건수/심각도
    // ... 기타 규제 데이터 필드들
}

/**
 * StateManager가 외부에 제공할 상태와 메타데이터를 통합합니다.
 */
export interface AuthorityContextValue {
    state: AuthorityState;
    currentLossEstimateUsd: number | null;
    message: string; // 사용자에게 보여줄 경고 메시지
}

/**
 * 초기 Context Value 정의
 */
export const initialAuthorityContext: AuthorityContextValue = {
    state: 'IDLE',
    currentLossEstimateUsd: 0,
    message: '시스템 대기 중. 규제 데이터 로딩을 시작하세요.',
};