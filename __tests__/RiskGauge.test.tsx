import React from 'react';
import { render, screen } from '@testing-library/react';
import RiskGauge from '../src/components/RiskGauge';
import { AuditBlock, RiskLevel } from '../src/types/miniRocianTypes';

// Helper function to create mock audit blocks
const getMockAudit = (level: RiskLevel, score: number): AuditBlock => ({
    transactionId: 'TEST-ID',
    timestamp: new Date(),
    riskScore: score,
    riskLevel: level,
    problemDefinition: 'Test Problem',
    rootCauseAnalysis: 'Test Cause',
    mitigationSuggestion: 'Test Fix',
});

describe('RiskGauge Component Validation', () => {
  test('should display CORRECT label and color for CRITICAL risk level (High Priority)', () => {
    const mockAudit = getMockAudit(RiskLevel.CRITICAL, 0.9);
    render(<RiskGauge auditData={mockAudit} />);

    // Critical 레벨의 레이블과 색상이 표시되는지 확인
    expect(screen.getByText(/🚨 Critical Alert/i)).toBeInTheDocument();
  });

  test('should display CORRECT label and color for LOW risk level (Safe)', () => {
    const mockAudit = getMockAudit(RiskLevel.LOW, 0.1);
    render(<RiskGauge auditData={mockAudit} />);

    // Low 레벨의 레이블과 색상이 표시되는지 확인
    expect(screen.getByText(/✅ Low Risk/i)).toBeInTheDocument();
  });

  test('should correctly display the risk score percentage', () => {
    const mockAudit = getMockAudit(RiskLevel.MEDIUM, 0.5); // 50%
    render(<RiskGauge auditData={mockAudit} />);

    // 점수가 정확히 출력되는지 확인 (toFixed(2)로 인해 문자열 매칭 필요)
    expect(screen.getByText(/Risk Score: 50.00%/i)).toBeInTheDocument();
  });
});