import { ComplianceViolation, ProofRecord } from '../types';

/**
 * @description 규제 위반 사례 데이터를 기반으로 A_LP(Avoided Loss Potential)를 계산하는 핵심 서비스 로직.
 * 이 함수는 스키마에 정의된 복잡한 산출 공식(Base Loss - Mitigation Factor) * Regulatory Multiplier를 구현합니다.
 * @param violationId: 위반 유형 ID (compliance_violation 테이블 참조)
 * @param payload: 실제 발생한 사건의 데이터 페이로드 (proof_record.payload)
 * @returns 계산된 A_LP 값
 */
export class ProofService {

    /**
     * 가상의 데이터를 기반으로 A_LP를 시뮬레이션하여 반환합니다.
     * 실제 환경에서는 DB에서 violation details와 loss history를 조회해야 합니다.
     * @param violationId 규정 위반 ID (DB 참조 필요)
     * @param payload 사건 페이로드 (실제 데이터가 포함된 JSONB)
     * @returns 계산된 $A_{LP}$ 값 (Number)
     */
    public static calculateALP(violationId: number, payload: Record<string, any>): number {
        // [⚠️ 경고] 이 부분은 실제 DB 연결 및 로직으로 대체되어야 합니다.
        console.log(`[INFO] Starting A_LP calculation for Violation ID: ${violationId}`);

        let baseLossPotential: number;
        let mitigationFactor: number;
        let regulatoryMultiplier: number;

        // 1. Base Loss Potential 추정 (데이터 유출 규모, 피해 범위 등)
        if (payload.scope === "EU-region" && payload.record_count >= 50000) {
            baseLossPotential = 500000.00; // 예: GDPR 최대 벌금 기준값
        } else if (payload.compromised_by?.includes("Bias")) {
            baseLossPotential = 30000.00; // 예: 편향성으로 인한 평판/법적 손실
        } else if (payload.scope === "Global" && payload.compromised_by?.includes("Audit Trail Tampering")) {
             baseLossPotential = 10000.00; // 예: 시스템 무결성 실패 시 벌금
        } else {
            // 기본값 또는 다른 로직 적용 (TODO)
            baseLossPotential = 5000.00;
        }

        // 2. Mitigation Factor 추정 (클라이언트의 대응 노력 및 회복 가능성)
        if (payload.mitigation_actions?.includes("암호화 재적용")) {
            mitigationFactor = baseLossPotential * 0.5; // 50% 감경 효과 가정
        } else if (violationId === 3 && payload.compromised_by?.includes("Audit Trail Tampering")) {
             mitigationFactor = 9000.00; // 특정 경우 고정값 설정
        } else {
            mitigationFactor = baseLossPotential * 0.1; // 기본 감경 (10%)
        }

        // 3. Regulatory Multiplier 적용 (법률의 엄격성 반영)
        if (violationId === 1) {
             regulatoryMultiplier = 2.0; // GDPR 등 고강도 규제일 경우 배율 증가
        } else if (violationId === 2) {
            regulatoryMultiplier = 1.66; // AI 편향성 위반의 높은 법적 책임 반영
        } else {
            regulatoryMultiplier = 1.0;
        }

        // 최종 계산: A_LP = (Base Loss - Mitigation Factor) * Multiplier
        const alp = Math.max(0, baseLossPotential - mitigationFactor) * regulatoryMultiplier;

        return parseFloat(alp.toFixed(2));
    }
}

export interface ComplianceViolation {
    violation_id: number;
    law_jurisdiction: string;
    relevant_act_name: string;
    regulatory_article: string;
    base_penalty_multiplier: number;
}