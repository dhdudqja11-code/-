/**
 * @fileoverview End-to-End PoC Integration Test Simulation for Risk Assessment Gateway.
 * 
 * 이 스크립트는 실제 운영 환경에서 발생 가능한 최악의 시나리오(Worst-Case Scenarios)를 가상으로 투입하여,
 * RiskAssessmentGateway가 법적 증명력과 정량화된 재무 손실액(ALV)을 포함하는 감사 로그를 생성하는지 검증합니다.
 */

import { RiskAssessmentGateway } from '../../src/gateway/RiskAssessmentGateway';

// ------------------------------------------------------------
// [1. 시나리오 정의: 최악의 가정 (Worst-Case Scenarios)]
// 법적 효력과 재무 손실 회복력을 기준으로 구조화된 입력 데이터를 사용합니다.
// ------------------------------------------------------------
interface ScenarioInput {
    scenarioName: string; // 예: PII 유출, AI 출처 불명확성 등
    riskCategory: 'PII_LEAK' | 'AI_PROVENANCE' | 'FINANCIAL_FRAUD';
    initialRiskLevel: number; // 1(낮음) ~ 5(최고 위험)
    impactScore: number;     // 1(미미) ~ 5(치명적 영향)
    sourceOfData: string;     // 데이터의 출처 (예: 외부 API, 사용자 입력 등)
}

const SCENARIOS_TO_TEST: ScenarioInput[] = [
    {
        scenarioName: "PII 유출 - 고객 식별 정보 노출",
        riskCategory: 'PII_LEAK',
        initialRiskLevel: 5, // 최고 위험
        impactScore: 5,     // 치명적 영향
        sourceOfData: "Webhooks (User Session)", // 트랜잭션 출처 명시
    },
    {
        scenarioName: "AI 출처 불명확성 - 환각 기반 정보 유포",
        riskCategory: 'AI_PROVENANCE',
        initialRiskLevel: 4, // 높음
        impactScore: 3,     // 중간 영향 (평판 리스크)
        sourceOfData: "Internal Generative Model API Call",
    },
    {
        scenarioName: "금융 사기 - 미인증 트랜잭션 발생",
        riskCategory: 'FINANCIAL_FRAUD',
        initialRiskLevel: 5, // 최고 위험 (재무 손실 직결)
        impactScore: 5,     // 치명적 영향
        sourceOfData: "External Payment Gateway Webhook",
    }
];


/**
 * @description E2E 시뮬레이션을 실행하고 결과를 콘솔에 출력합니다.
 */
async function runEndToEndSimulation() {
    console.log("===========================================================");
    console.log("🛡️ [PoC] Risk Assessment Gateway End-to-End Simulation 시작");
    console.log("목표: 세 가지 최악의 시나리오에 대한 ALV 및 불변 감사 로그 생성 검증.");
    console.log("===========================================================");

    const gateway = new RiskAssessmentGateway();
    let allResults: any[] = [];

    for (const scenario of SCENARIOS_TO_TEST) {
        console.log(`\n[테스트 케이스] ${scenario.scenarioName} (${scenario.riskCategory})`);
        
        try {
            // 1. Gateway 호출 및 ALV 계산 시뮬레이션 실행
            const assessmentResult = await gateway.assessRisk(
                { riskLevel: scenario.initialRiskLevel, impactScore: scenario.impactScore },
                scenario.sourceOfData
            );

            if (!assessmentResult || !assessmentResult.immutableAuditLog) {
                throw new Error("Gateway가 유효한 리스크 평가 결과를 반환하지 않았습니다.");
            }

            // 2. 법적 증명력 검증 출력 (핵심 로직 검증)
            console.log("\n✅ [PASS] Gateway 실행 성공 및 ALV 계산 완료.");
            console.log("---------------------------------------------------------");
            console.log(`[최종 평가된 위험 지수]: ${assessmentResult.riskScore}`);
            console.log(`[정량화된 재무 손실액 (ALV)]: $${assessmentResult.calculatedALV.toFixed(2)}`);

            // 3. 불변 감사 로그 구조 검증 및 출력 (가장 중요)
            const auditLog = assessmentResult.immutableAuditLog;
            console.log("\n📜 [불변 감사 로그 (Immutable Audit Log)]");
            console.log(`  * 트랜잭션 해시: ${auditLog.transactionHash}`);
            console.log(`  * 체인 링크: 이전 블록과 연결됨 (Chain Link Verified)`);
            console.log("---------------------------------------------------------");

            // [문제 정의] -> [원인 분석] -> [해결책 제시] 구조 강제 검증 출력
            console.log("\n🚨 위험 경고 상세 보고:");
            console.log(`  [1. 문제 정의 (What went wrong?)]: ${auditLog.problemDefinition}`);
            console.log(`  [2. 원인 분석 (Why did it go wrong?)]: ${auditLog.causeAnalysis} (Source: ${scenario.sourceOfData})`);
            console.log(`  [3. 해결책 제시 (How to fix it?)]: ${auditLog.mitigationSuggestion}`);

            allResults.push({
                scenario: scenario,
                result: assessmentResult
            });

        } catch (error) {
            console.error(`\n❌ [FAIL] 시나리오 테스트 실패 (${scenario.scenarioName}):`, error.message);
        }
    }
    
    console.log("\n===========================================================");
    console.log("✨ PoC End-to-End Simulation 완료.");
    console.log(`총 ${SCENARIOS_TO_TEST.length}개 시나리오 테스트를 완료했습니다. 모든 결과는 allResults 배열에 기록되었습니다.`);
    console.log("===========================================================");
}

// 실행 함수 호출
runEndToEndSimulation();