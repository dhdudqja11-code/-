/**
 * Mini ROI 시뮬레이션 API 응답 스키마 정의
 * (모든 데이터는 숫자 형태로 오지만, 강제 형변환 및 null 체크가 필수입니다.)
 */

export type SimulationResult = {
    riskGrade: 'Low' | 'Medium' | 'High' | 'Critical'; // 핵심 위험 등급
    estimatedLossAmountUSD: number; // 추정 재무 손실액 (달러 기준)
    mitigationActionPlan: string[]; // 제시된 해결책 리스트
    sourceDataVerification?: {
        source: string; // 데이터 출처
        verificationTime: Date; // 검증 시점
        isVerifiedBySystem: boolean; // 시스템 인증 여부
    }
};

export type SimulationError = {
    errorCode: number;
    message: string; // 사용자에게 보여줄 에러 메시지
    details?: Record<string, any>; // 상세 디버깅 정보
};

/**
 * 시뮬레이션 입력 파라미터 스키마
 */
export type SimulationInputParams = {
    industry: string;
    marketSizeMillionsUSD: number; // 시장 규모 (백만 USD)
    regulatoryComplianceScore: number; // 규제 준수 점수 (0~100)
};

/**
 * 훅의 최종 상태 타입을 정의합니다.
 */
export type SimulationHookState = {
    data: SimulationResult | null;
    error: SimulationError | null;
    isLoading: boolean;
    params: SimulationInputParams; // 사용자가 입력한 파라미터
};