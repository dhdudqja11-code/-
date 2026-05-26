export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface AuditBlock {
  transactionId: string; // 트랜잭션 고유 ID (Immutable Proof)
  timestamp: Date;       // 감사 시점 (Verification Time)
  riskScore: number;     // 0.0 ~ 1.0 사이의 위험 점수
  riskLevel: RiskLevel;  // 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL' 중 하나
  problemDefinition: string; // [문제 정의] What went wrong? (법적/재무적 문제)
  rootCauseAnalysis: string; // [원인 분석] Why did it go wrong? Source/Time.
  mitigationSuggestion: string; // [해결책 제시] How to fix it? (구체적인 행동 지침)
}

export interface ALVData {
    estimatedLossAmountUSD: number; // 추정 손실액 (ALV Core Metric)
    impactScore: number;           // 영향도 점수 (0~100)
    mitigationRequiredYears: number; // 완화 필요 기간 (년)
}

export interface MiniRocianState {
    auditBlock?: AuditBlock;
    alvData?: ALVData;
    isLoading: boolean;
    hasCriticalAlert: boolean;
}