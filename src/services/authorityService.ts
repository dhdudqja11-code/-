/**
 * @description [Authority Service] 규제 리스크 데이터를 받아 시스템적 통제권을 계산하고, 
 *              결과에 따라 '권위적인 상태 메시지'를 반환하는 서비스 레이어입니다.
 * @param {Object} regulatoryData - 외부에서 수신된 법률/재무 리스크 데이터 (v2.0 스키마 가정).
 * @returns {Promise<{status: 'RESOLVED' | 'WARNING' | 'CRITICAL'; message: string; details: Object}>}
 */
export async function calculateAuthorityStatus(regulatoryData: any): Promise<any> {
    // 1. 입력값 검증 (Guard Clause) - 데이터 유효성 및 스키마 체크가 최우선입니다.
    if (!regulatoryData || typeof regulatoryData !== 'object') {
        throw new Error("Invalid input data structure provided to Authority Checker.");
    }

    const financialImpact = parseFloat(regulatoryData?.financial_impact ?? 0);
    const violationCount = Number(Object.keys(regulatoryData?.violations || {}).length);

    // 2. 리스크 임계값 정의 및 상태 결정 (Core Logic)
    let status: 'RESOLVED' | 'WARNING' | 'CRITICAL';
    let message: string;
    let details: { regulatoryDetails: any, recoveryPlan: any };

    if (financialImpact > 5000 || violationCount >= 3) {
        status = 'CRITICAL';
        message = "🚨 심각한 법률/재무 리스크 감지. 즉각적인 시스템 개입과 권위적 해결책 제시가 필요합니다.";
        details = {
            regulatoryDetails: regulatoryData.violations || {},
            recoveryPlan: { 
                mitigationAction: "최소화된 피해 확산을 위해 전담 법률/재무팀의 검토를 요청합니다.", 
                suggestedSolution: "Compliance Meter 기반의 상세 진단 보고서를 즉시 발급받으십시오." 
            }
        };
    } else if (financialImpact > 50 || violationCount >= 1) {
        status = 'WARNING';
        message = "⚠️ 규제 준수 필요. 데이터 분석 결과, 잠재적 리스크가 감지되었습니다. 시스템 개입을 통해 통제권을 회복해야 합니다.";
        details = {
            regulatoryDetails: regulatoryData.violations || {},
            recoveryPlan: { 
                mitigationAction: "해당 위반 사례의 법률 근거를 재검토하고, 프로세스를 표준화하십시오.", 
                suggestedSolution: "데이터 출처와 검증 시점을 명확히 기록하는 절차가 필수적입니다." 
            }
        };
    } else {
        status = 'RESOLVED';
        message = "✅ 현재 시스템은 모든 법률 및 재무 리스크를 성공적으로 모니터링하고 있습니다. 통제권이 확보되었습니다.";
        details = { regulatoryDetails: {}, recoveryPlan: { mitigationAction: null, suggestedSolution: null } };
    }

    // 3. 결과 반환 (Output Structure Enforcement) - 반드시 구조화된 JSON을 준수해야 합니다.
    return { status, message, details };
}

/**
 * @description API 호출 실패 시 발생하는 권위적인 경고(Authority Warning) 메시지 생성 유틸리티.
 */
export function generateFailureWarning(error: Error): string {
    // 시스템적 통제권 회복을 강조합니다.
    return `[SYSTEM ERROR]: 데이터 처리 중 치명적인 오류가 발생했습니다. (${error.name}: ${error.message}). 
    현재 시스템은 데이터를 재검증하고 권위적 상태로 복구하는 과정에 있습니다. 
    사용자께서는 잠시 후 안내되는 [해결책 제시]를 참고하여 다음 단계를 진행해주십시오.`;
}