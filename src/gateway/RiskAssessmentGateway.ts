/**
 * @module RiskAssessmentGateway
 * @description 가상의 트랜잭션 데이터에 대한 법적 무결성 검증 및 재무 손실액(ALV) 산정 게이트웨이.
 * 핵심 목표: 위험 발생 시 [문제 정의 → 원인 분석 → 해결책 제시]의 3단계 보고서 구조를 강제함.
 */

import { AuditBlock, TransactionData } from "./types";
import { generateHashChain } from "./audit/AuditLogService";

// Mock ALV Calculation (실제 비즈니스 로직이 들어갈 자리)
/**
 * 주어진 위험 레벨과 영향도를 기반으로 예상되는 재무 손실액(ALV)을 산정합니다.
 * @param riskLevel - 1 (낮음) ~ 5 (매우 높음)
 * @param impactScore - 데이터의 핵심 가치 손실 점수 (0~100)
 * @returns ALV 금액 (KRW)와 위험 등급
 */
export const calculateALV = (riskLevel: number, impactScore: number): { alvAmount: number; riskGrade: string } => {
    // 1. Risk Level에 따른 기본 가중치 설정
    const baseLossFactor = Math.pow(riskLevel, 2) * 500000; // 레벨이 높을수록 기하급수적 손실 발생 가정

    // 2. Impact Score 반영 (데이터의 중요성)
    const impactMultiplier = impactScore / 100; 

    // 최종 ALV 계산: 기본 손실 * 영향도 계수 * 무작위 변동계수(가정)
    let alvAmount = Math.floor(baseLossFactor * impactMultiplier * (1 + Math.random() * 0.2));

    if (alvAmount < 1000000) {
        // 최소한의 경고 금액 보장
        alvAmount = 1000000; 
    }

    let riskGrade: string;
    if (riskLevel >= 4 || alvAmount > 50_000_000) {
        riskGrade = "Critical"; // 법적 분쟁 가능성 높음
    } else if (riskLevel >= 2 && alvAmount > 10_000_000) {
        riskGrade = "High"; // 규제 위반 우려 있음
    } else {
        riskGrade = "Low";
    }

    return { alvAmount: Math.floor(alvAmount), riskGrade };
};


/**
 * 위험 평가 게이트웨이 서비스의 메인 클래스.
 * 트랜잭션 무결성을 검사하고, 문제가 발생하면 ALV 기반의 보고서를 생성합니다.
 */
export class RiskAssessmentGateway {
    constructor() {}

    /**
     * 가상 트랜잭션을 처리하고 리스크 평가 결과를 반환하는 핵심 로직.
     * @param transactionData - 외부에서 수신된 트랜잭션 데이터 (예: Webhook Payload).
     * @returns AssessmentResult 객체 또는 오류 보고서.
     */
    public async assessRiskAndGenerateReport(transactionData: TransactionData): Promise<{ success: boolean; report: any }> {
        console.log(`[INFO] Assessing risk for transaction source: ${transactionData.source}`);

        // 1. 법적 무결성 검증 (가정)
        const isValid = this.isTransactionIntegrityValid(transactionData);

        if (!isValid) {
            // 🚨 위험 감지! AuditBlock 생성을 시도하지만 실패함.
            const riskLevel = 5; // 최고 위험 레벨 가정
            const impactScore = Math.min(100, (Math.random() * 4 + 2) * 25); // 임의로 높게 설정

            // ALV 계산 실행
            const { alvAmount: estimatedAlv, riskGrade } = calculateALV(riskLevel, impactScore);

            // 3단계 보고서 생성 (핵심 지시사항 반영)
            const report = this.generateThreeStageReport(estimatedAlv, riskGrade, transactionData);
            return { success: false, report };

        } else {
             // 무결성 정상 처리 시의 성공적인 감사 로그 기록 로직
            try {
                const auditBlock = { 
                    timestamp: new Date().toISOString(), 
                    dataHash: 'SUCCESS_HASH', 
                    prevHash: 'MOCK_PREV_HASH' 
                };
                generateHashChain(auditBlock); // 로그 성공적으로 생성됨 가정

                return { success: true, report: { message: "Transaction integrity verified. Audit log recorded successfully.", alvEstimate: 0 } };
            } catch (e) {
                console.error("Audit Log Failure:", e);
                // 시스템 자체 문제로 인한 실패도 경고해야 함
                const fallbackReport = this.generateThreeStageReport(10_000_000, "System", transactionData);
                 return { success: false, report: fallbackReport };
            }
        }
    }

    /**
     * 가상의 무결성 검사 함수. 특정 조건을 만족하지 못하면 실패를 반환합니다. (Danger Path 유발)
     */
    private isTransactionIntegrityValid(data: TransactionData): boolean {
        // 예시 1: 필수 데이터 누락 체크
        if (!data.source || !data.payload) return false;

        // 예시 2: 규제 준수 여부 검증 (가정) - 만약 'HIPAA'나 특정 키워드가 들어오면 무효 처리 가정
        const forbiddenKeywords = ['unencrypted', 'raw_pci'];
        for (const keyword of forbiddenKeywords) {
            if (data.payload.includes(keyword)) {
                console.warn(`[WARNING] Forbidden keyword detected: ${keyword}. Data rejected.`);
                return false; 
            }
        }

        return true;
    }


    /**
     * 법적 무결성 문제 발생 시, 구조화된 [문제 정의 → 원인 분석 → 해결책 제시] 보고서를 생성합니다.
     */
    private generateThreeStageReport(alv: number, grade: string, data: TransactionData): any {
        return {
            riskGrade: grade,
            estimatedAnnualLossValue: alv, // 핵심 시각화 요소
            reportStructure: {
                // 1. 문제 정의 (What went wrong?) - 공포 조성 단계
                problemDefinition: `🚨 Critical Integrity Failure Detected! (${grade} Risk)`,
                description: "수신된 트랜잭션 데이터는 법적 증명 가능성(Legal Proof)을 담보하지 못하는 심각한 무결성 결함을 보입니다. 이대로 진행할 경우, 회사는 막대한 재정 손실에 직면합니다.",

                // 2. 원인 분석 (Why did it go wrong? Source/Time) - 기술적 근거 제시
                causeAnalysis: `Source: ${data.source} | Time: ${new Date().toISOString()}`,
                detail: "데이터 페이로드 내에서 필수 규제 필드(예: 암호화 키, 사용자 동의 플래그 등)가 누락되거나 위변조된 흔적이 발견되었습니다. 이는 체인 해싱 기반 감사 로그 생성 자체를 불가능하게 만듭니다.",

                // 3. 해결책 제시 (How to fix it?) - 제품 가치 전환점
                mitigationSuggestion: "✅ [Mini ROI Simulator Gateway]를 통해 즉시 사후 진단 및 리스크 재산정 과정을 거쳐야 합니다. 시스템은 누락된 데이터를 자동으로 보완하고, 법적 무결성을 확보하는 '해결책 제시(Mitigation Suggestion)' 기능을 제공합니다.",
                requiredAction: "즉시 관리자 대시보드에서 상세 분석을 요청하십시오."
            }
        };
    }
}