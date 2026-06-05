/**
 * @description 리서처님이 제공한 L_reg 데이터를 타입 안전하게 정의합니다.
 * 이 구조는 모든 $L_{reg}$ 관련 컴플라이언스 데이터의 최소 스키마입니다.
 */
export interface ComplianceRiskData {
    No: number; // No. 1, 2, 3...
    'Risk Type': string; // 위험 유형 (e.g., Right-to-Erasure Failure)
    'Regulatory Basis': string; // 규제 근거/위반 상황 (e.g., GDPR Article 17)
    'Pain Point': string; // 구체적 위반 사례 및 설명
    'Worst-Case L': string; // 최소 예상 벌금 범위 (문자열로 처리하여 정규식 분석 유도)
    'Required Proof Point': string; // 필수 증명 요소
}

// AuthorityMeter 컴포넌트가 사용할 더미 타입 (실제로는 Props를 정의해야 함)
export interface AuthorityMeterProps {
    score: number; // 0.0 ~ 1.0 사이의 통제권 안정성 지표
    status: 'SAFE' | 'WARNING' | 'CRITICAL';
}