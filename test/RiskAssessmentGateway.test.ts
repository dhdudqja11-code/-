import { RiskAssessmentGateway, calculateALV } from "../src/gateway/RiskAssessmentGateway";

// Mocking the AuditLogService to prevent actual file writing during unit tests
jest.mock("../src/gateway/audit/AuditLogService", () => ({
    generateHashChain: jest.fn(),
}));

describe('RiskAssessmentGateway - Legal Integrity & ALV Simulation', () => {
    let gateway: RiskAssessmentGateway;
    const mockSuccessData = { source: "PayPal_Webhook", payload: '{"user_id": 123, "status": "paid"}' };
    const mockDangerData = { source: "ExternalAPI_Bad", payload: 'unencrypted data with raw_pci keyword' };

    beforeEach(() => {
        gateway = new RiskAssessmentGateway();
        // Mock the generateHashChain function before each test run
        jest.clearAllMocks();
    });

    it('✅ should successfully process and log transaction if integrity is maintained (Golden Path)', async () => {
        const result = await gateway.assessRiskAndGenerateReport(mockSuccessData);
        
        // 1. 성공적으로 처리되었는지 확인
        expect(result.success).toBe(true);
        // 2. AuditLogService가 호출되어야 함 (로그 기록 성공)
        expect(require("../src/gateway/audit/AuditLogService").generateHashChain).toHaveBeenCalledTimes(1);
    });

    it('❌ should detect integrity failure, calculate ALV, and generate the 3-stage report (Danger Path)', async () => {
        // Danger Data는 unencrypted와 raw_pci 키워드를 포함하여 실패가 예상됨.
        const result = await gateway.assessRiskAndGenerateReport(mockDangerData);

        // 1. 위험 감지 및 실패 보고서 반환 확인
        expect(result.success).toBe(false);
        const report = result.report;
        
        // 2. ALV가 계산되었는지, 그리고 값이 유효한 범위 내에 있는지 확인 (최소 금액 보장 테스트)
        expect(typeof report.estimatedAnnualLossValue).toBe('number');
        expect(report.estimatedAnnualLossValue).toBeGreaterThanOrEqual(1_000_000);

        // 3. 보고서 구조가 강제되었는지 확인 (3단계 필수 요소 체크)
        const structure = report.reportStructure;
        expect(structure).toHaveProperty('problemDefinition'); // [문제 정의] 존재 여부
        expect(structure).toHaveProperty('causeAnalysis');     // [원인 분석] 존재 여부
        expect(structure).toHaveProperty('mitigationSuggestion');// [해결책 제시] 존재 여부
    });

    it('💰 calculateALV should correctly adjust ALV based on risk level and impact score', () => {
        // 낮은 레벨 테스트 (기준점)
        const lowAlv = calculateALV(1, 10);
        expect(lowAlv.riskGrade).toBe("Low");
        expect(lowAlv.alvAmount).toBeGreaterThanOrEqual(1_000_000);

        // 높은 레벨 테스트 (크리티컬)
        const highAlv = calculateALV(5, 90);
        expect(highAlv.riskGrade).toBe("Critical");
        // ALV가 초기 기준보다 훨씬 높게 계산되는지 확인 (단순 검증)
        expect(highAlv.alvAmount).toBeGreaterThan(10_000_000); 
    });
});