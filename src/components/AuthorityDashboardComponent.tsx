// src/components/AuthorityDashboardComponent.tsx
import React, { useState } from 'react';

/**
 * -----------------------------------------------------
 * [TYPE DEFINITIONS] 데이터 스키마 정의 (v3.0 규격 반영)
 * -----------------------------------------------------
 */

export interface LegalRiskData {
  source: string; // 리스크 데이터의 출처 (예: GDPR-2018)
  severityScore: number; // 심각도 점수 (0.0 ~ 1.0)
  violationMechanism: string; // 위반 메커니즘 설명
  potentialFailures?: Array<{ field: string; value: any }>;
}

export interface AIBiasStatus {
  is_biased: boolean;
  data_provenance_trace: string;
  highest_risk_group: string | null;
  bias_score: number;
  compliance_evidence: string;
}

export interface SovereigntyStatus {
  is_compliant: boolean;
  conflict_detected: boolean;
  conflicting_jurisdictions: string[];
  data_flow_path_used: string;
  legal_proof_attached: boolean;
}

export interface ESGRiskStatus {
  is_compliant: boolean;
  primary_violation: string | null;
  cso_score: number;
  mitigation_plan_verified: boolean;
  estimated_financial_impact_usd: number;
}

export interface RiskMetrics {
  ai_bias_status: AIBiasStatus;
  sovereignty_status: SovereigntyStatus;
  esg_risk_status: ESGRiskStatus;
}

export interface SummaryReport {
  compliance_status: string;
  total_risk_score: number;
  authority_warning: Record<string, any>;
  mitigation_plan: string[];
}

export interface AuthorityResponse {
  status: string; // 'COMPLIANT' | 'WARNING' | 'NON_COMPLIANT'
  timestamp: string;
  overall_compliance_score: number;
  risk_metrics: RiskMetrics;
  summary_report: SummaryReport;
}

interface LegalRiskProps {
  riskData: LegalRiskData;
  initialAuthorityStatus?: 'UNKNOWN' | 'SAFE' | 'WARNING' | 'NON_COMPLIANT'; 
}

/**
 * [Core Component] v3.0 글로벌 리스크 데이터를 시각화하고 실시간 통제권을 확인하는 대시보드 컴포넌트
 */
const AuthorityDashboardComponent: React.FC<LegalRiskProps> = ({ 
  riskData, 
  initialAuthorityStatus = 'UNKNOWN' 
}) => {
  const [apiResponse, setApiResponse] = useState<AuthorityResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  /**
   * 핵심 로직: 실제 API 호출 지점 (POST /api/v1/check_authority)
   */
  const handleAuthorityCheck = async () => {
    if (!riskData || riskData.severityScore === undefined) {
      setErrorMsg("🚨 검사할 법률 리스크 데이터가 부족합니다. 스키마를 확인하세요.");
      return;
    }

    setIsProcessing(true);
    setErrorMsg(null);
    setApiResponse(null);

    // v3.0 규격에 맞는 페이로드 조립
    const payload = {
      regulatory_cases: [
        {
          article_id: riskData.source || "REG-UNKNOWN",
          violation_type: riskData.violationMechanism || "미설정 규정 위반 가능성",
          risk_category: "법률",
          severity_score: riskData.severityScore,
          estimated_financial_loss: (riskData.potentialFailures?.length || 0) * 15000.0
        }
      ],
      financial_params: {
        revenue: 15000000,
        users: 12500
      },
      // 동적으로 리스크 데이터를 입력 데이터로 매핑
      ai_bias_input: {
        is_biased: riskData.severityScore > 0.6,
        data_provenance_trace: "TR-" + Math.floor(Math.random() * 90000 + 10000),
        highest_risk_group: riskData.severityScore > 0.6 ? "Gender/Age Under-representation" : null,
        bias_score: parseFloat((riskData.severityScore * 0.75).toFixed(2)),
        compliance_evidence: "Proof_of_Training_Dataset_V3"
      },
      sovereignty_input: {
        is_compliant: riskData.severityScore < 0.8,
        conflict_detected: riskData.severityScore > 0.7,
        conflicting_jurisdictions: riskData.severityScore > 0.7 ? ["China PIPL", "EU GDPR"] : [],
        data_flow_path_used: "Anon_Gateway_Singapore",
        legal_proof_attached: true
      },
      esg_input: {
        is_compliant: riskData.severityScore < 0.5,
        primary_violation: riskData.severityScore > 0.5 ? "Carbon Emission Exceedance" : null,
        cso_score: Math.round(100 - riskData.severityScore * 40),
        mitigation_plan_verified: true,
        estimated_financial_impact_usd: riskData.severityScore > 0.5 ? 1200000.0 : 50000.0
      }
    };

    try {
      const response = await fetch('/api/v1/check_authority', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = (await response.json()) as AuthorityResponse;
      setApiResponse(data);
    } catch (error: any) {
      setErrorMsg("⚠️ 통제권 재확립 중... 백엔드 API 서버에 연결할 수 없습니다. 로컬 서버(authority_api) 기동 상태를 확인해 주십시오.");
      console.error("[Error] Authority Check Failed:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  // 상태에 따른 컬러 매핑
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLIANT': return '#00ff87'; // Vibrant neon green
      case 'WARNING': return '#f1c40f'; // Bright yellow
      case 'NON_COMPLIANT':
      case 'CRITICAL': return '#ff0055'; // Intense red-pink
      default: return '#7f8c8d';
    }
  };

  return (
    <div style={styles.container}>
      {/* Glitch & Custom Animation CSS Injection */}
      <style dangerouslySetInnerHTML={{ __html: glitchStyles }} />

      <h1 style={styles.title}>🛡️ Systemic Authority Dashboard <span style={styles.badge}>v3.0</span></h1>
      <p style={styles.subtitle}>인공지능 편향, 지정학적 데이터 주권 충돌, ESG 준수 여부를 포함한 실시간 통제성 확보 시스템</p>

      {/* 1. 기본 리스크 인풋 요약 */}
      <div style={styles.metricGrid}>
        <div style={styles.metricCard}>
          <span style={styles.cardLabel}>검사 대상 법적 근거</span>
          <strong style={styles.cardValue}>{riskData?.source || 'N/A'}</strong>
        </div>
        <div style={styles.metricCard}>
          <span style={styles.cardLabel}>입력 심각도 가중치</span>
          <strong style={{ ...styles.cardValue, color: riskData?.severityScore > 0.6 ? '#ff0055' : '#00ff87' }}>
            {(riskData?.severityScore || 0).toFixed(2)}
          </strong>
        </div>
        <div style={styles.metricCard}>
          <span style={styles.cardLabel}>잠재적 예외 필드 수</span>
          <strong style={styles.cardValue}>{riskData?.potentialFailures?.length || 0}개</strong>
        </div>
      </div>

      {/* 2. 실시간 검증 트리거 및 진단기 */}
      <div style={styles.actionBox}>
        <div style={styles.boxHeader}>
          <h3>🔗 E2E Authority Verification</h3>
          <button 
            onClick={handleAuthorityCheck} 
            disabled={isProcessing}
            style={{ 
              ...styles.checkButton,
              backgroundColor: isProcessing ? '#4a5568' : '#0070f3',
              boxShadow: isProcessing ? 'none' : '0 4px 14px 0 rgba(0, 118, 243, 0.39)'
            }}
          >
            {isProcessing ? '진단서 분석 및 통제권 회복 중...' : '시스템 권위 검사 가동 (v3.0)'}
          </button>
        </div>

        {/* 에러 발생 시 경고 영역 */}
        {errorMsg && (
          <div style={styles.errorContainer} className="glitch-card">
            <span style={{ fontSize: '1.2rem', marginRight: '10px' }}>⚠️</span>
            <p style={styles.errorText} className="glitch-text">{errorMsg}</p>
          </div>
        )}

        {/* 3. API Response가 있는 경우 렌더링 */}
        {apiResponse && (
          <div style={styles.resultContainer}>
            <div style={styles.resultSummary}>
              <div>
                <span style={styles.sectionLabel}>종합 판단 상태</span>
                <div style={{ ...styles.statusDisplay, color: getStatusColor(apiResponse.status) }}>
                  {apiResponse.status}
                </div>
              </div>
              <div>
                <span style={styles.sectionLabel}>전체 컴플라이언스 점수</span>
                <div style={styles.scoreDisplay}>
                  {Math.round(apiResponse.overall_compliance_score * 100)}%
                </div>
              </div>
              <div>
                <span style={styles.sectionLabel}>검증 시간 (UTC)</span>
                <div style={styles.timeDisplay}>
                  {new Date(apiResponse.timestamp).toLocaleString()}
                </div>
              </div>
            </div>

            {/* 신규 v3.0 글로벌 리스크 메트릭 카드 레이아웃 */}
            <h4 style={styles.sectionTitle}>🌐 Global Risk Metrics Details</h4>
            <div style={styles.metricsGrid}>
              
              {/* A. AI 편향 분석 카드 */}
              <div 
                style={styles.metricDetailCard}
                className={apiResponse.risk_metrics.ai_bias_status.is_biased ? "glitch-card" : ""}
              >
                <div style={styles.cardHeader}>
                  <h4>🤖 AI Provenance & Bias</h4>
                  <span style={{ 
                    ...styles.statusBadge, 
                    backgroundColor: apiResponse.risk_metrics.ai_bias_status.is_biased ? 'rgba(255, 0, 85, 0.2)' : 'rgba(0, 255, 135, 0.2)',
                    color: apiResponse.risk_metrics.ai_bias_status.is_biased ? '#ff0055' : '#00ff87'
                  }}>
                    {apiResponse.risk_metrics.ai_bias_status.is_biased ? "BIASED DETECTED" : "COMPLIANT"}
                  </span>
                </div>
                <p style={styles.detailRow}><strong>편향 지수:</strong> {apiResponse.risk_metrics.ai_bias_status.bias_score}</p>
                <p style={styles.detailRow}><strong>추적 ID:</strong> <code style={styles.code}>{apiResponse.risk_metrics.ai_bias_status.data_provenance_trace}</code></p>
                {apiResponse.risk_metrics.ai_bias_status.highest_risk_group && (
                  <p style={styles.detailRow}><strong>취약 타겟:</strong> {apiResponse.risk_metrics.ai_bias_status.highest_risk_group}</p>
                )}
                <p style={styles.detailRow}><strong>보증 증명:</strong> <span style={styles.linkText}>{apiResponse.risk_metrics.ai_bias_status.compliance_evidence}</span></p>
              </div>

              {/* B. 데이터 주권 분석 카드 */}
              <div style={styles.metricDetailCard}>
                <div style={styles.cardHeader}>
                  <h4>⚖️ Data Sovereignty</h4>
                  <span style={{ 
                    ...styles.statusBadge, 
                    backgroundColor: apiResponse.risk_metrics.sovereignty_status.conflict_detected ? 'rgba(241, 196, 15, 0.2)' : 'rgba(0, 255, 135, 0.2)',
                    color: apiResponse.risk_metrics.sovereignty_status.conflict_detected ? '#f1c40f' : '#00ff87'
                  }}>
                    {apiResponse.risk_metrics.sovereignty_status.conflict_detected ? "CONFLICT DETECTED" : "SECURED"}
                  </span>
                </div>
                <p style={styles.detailRow}><strong>전송 경로:</strong> <code style={styles.code}>{apiResponse.risk_metrics.sovereignty_status.data_flow_path_used}</code></p>
                <p style={styles.detailRow}><strong>법적 에스크로 보관:</strong> {apiResponse.risk_metrics.sovereignty_status.legal_proof_attached ? "첨부됨 (불변 보증)" : "미제출"}</p>
                {apiResponse.risk_metrics.sovereignty_status.conflict_detected && (
                  <p style={{ ...styles.detailRow, color: '#f1c40f' }}>
                    <strong>충돌 법규:</strong> {apiResponse.risk_metrics.sovereignty_status.conflicting_jurisdictions.join(", ")}
                  </p>
                )}
              </div>

              {/* C. ESG 감사 카드 (대규모 피해 시 네온 보더 강조) */}
              <div 
                style={styles.metricDetailCard}
                className={apiResponse.risk_metrics.esg_risk_status.estimated_financial_impact_usd >= 1000000.0 ? "neon-border" : ""}
              >
                <div style={styles.cardHeader}>
                  <h4>🌳 ESG Compliance Audit</h4>
                  <span style={{ 
                    ...styles.statusBadge, 
                    backgroundColor: apiResponse.risk_metrics.esg_risk_status.is_compliant ? 'rgba(0, 255, 135, 0.2)' : 'rgba(255, 0, 85, 0.2)',
                    color: apiResponse.risk_metrics.esg_risk_status.is_compliant ? '#00ff87' : '#ff0055'
                  }}>
                    {apiResponse.risk_metrics.esg_risk_status.is_compliant ? "COMPLIANT" : "NON-COMPLIANT"}
                  </span>
                </div>
                <p style={styles.detailRow}><strong>CSO 환경 점수:</strong> {apiResponse.risk_metrics.esg_risk_status.cso_score}/100</p>
                <p style={styles.detailRow}><strong>완화 계획 확인:</strong> {apiResponse.risk_metrics.esg_risk_status.mitigation_plan_verified ? "검증 완료" : "미승인"}</p>
                {apiResponse.risk_metrics.esg_risk_status.primary_violation && (
                  <p style={{ ...styles.detailRow, color: '#ff0055' }}><strong>위반 항목:</strong> {apiResponse.risk_metrics.esg_risk_status.primary_violation}</p>
                )}
                <div style={styles.financialImpactBox}>
                  <span>정량적 추정 재무 손실액 (USD):</span>
                  <strong style={{ fontSize: '1.25rem', color: apiResponse.risk_metrics.esg_risk_status.estimated_financial_impact_usd >= 1000000.0 ? '#ff0055' : '#ffffff' }}>
                    ${apiResponse.risk_metrics.esg_risk_status.estimated_financial_impact_usd.toLocaleString()}
                  </strong>
                </div>
              </div>

            </div>

            {/* 기존 2.0 호환 대응 조치 계획서 */}
            <div style={styles.mitigationBox}>
              <h4 style={{ margin: '0 0 10px 0', color: '#ff0055' }}>🚨 통제 및 리스크 완화 시나리오 (Mitigation Strategy)</h4>
              <ul style={styles.mitigationList}>
                {apiResponse.summary_report.mitigation_plan.map((plan, i) => (
                  <li key={i} style={styles.mitigationItem}>{plan}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* API 미호출 시 스켈레톤 상태 */}
        {!apiResponse && !isProcessing && (
          <div style={styles.placeholderBox}>
            <p>위의 `시스템 권위 검사 가동` 버튼을 탭하여 실시간 검증을 시행해 주십시오.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// CSS Styles (Premium Dark Glassmorphism)
const styles: { [key: string]: React.CSSProperties } = {
  container: { 
    fontFamily: '"Inter", "Outfit", -apple-system, sans-serif', 
    maxWidth: '1200px', 
    margin: '40px auto', 
    padding: '40px',
    backgroundColor: '#0a0d14', 
    borderRadius: '24px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
    color: '#f3f4f6',
    border: '1px solid #1f2937'
  },
  title: { 
    fontSize: '2.5rem', 
    fontWeight: 800, 
    margin: '0 0 10px 0',
    background: 'linear-gradient(to right, #ffffff, #9ca3af)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    display: 'flex',
    alignItems: 'center',
    gap: '15px'
  },
  badge: {
    fontSize: '1rem',
    padding: '4px 10px',
    borderRadius: '8px',
    backgroundColor: '#1e293b',
    border: '1px solid #3b82f6',
    color: '#3b82f6',
    fontStyle: 'normal',
    fontWeight: 'normal' as any
  },
  subtitle: { 
    fontSize: '1.1rem', 
    color: '#9ca3af', 
    margin: '0 0 40px 0',
    lineHeight: '1.6'
  },
  metricGrid: { 
    display: 'grid', 
    gridTemplateColumns: 'repeat(3, 1fr)', 
    gap: '20px', 
    marginBottom: '40px' 
  },
  metricCard: { 
    padding: '24px', 
    backgroundColor: '#111827', 
    borderRadius: '16px', 
    border: '1px solid #1f2937',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  cardLabel: { 
    fontSize: '0.875rem', 
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
  },
  cardValue: { 
    fontSize: '1.5rem', 
    fontWeight: 700 
  },
  actionBox: { 
    border: '1px solid #1f2937', 
    padding: '40px', 
    borderRadius: '20px', 
    backgroundColor: '#111827' 
  },
  boxHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '30px',
    flexWrap: 'wrap',
    gap: '20px'
  },
  checkButton: { 
    padding: '16px 32px', 
    fontSize: '1.05em', 
    fontWeight: 600,
    cursor: 'pointer', 
    color: 'white', 
    border: 'none', 
    borderRadius: '12px', 
    transition: 'all 0.3s ease',
  },
  errorContainer: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 0, 85, 0.1)',
    border: '1px solid #ff0055',
    padding: '20px',
    borderRadius: '12px',
    marginBottom: '30px'
  },
  errorText: {
    color: '#ff4d79',
    fontWeight: 'bold',
    margin: 0
  },
  resultContainer: {
    animation: 'fadeIn 0.5s ease-in-out'
  },
  resultSummary: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '30px',
    backgroundColor: '#1e293b',
    padding: '30px',
    borderRadius: '16px',
    border: '1px solid #334155',
    marginBottom: '40px'
  },
  sectionLabel: {
    fontSize: '0.85rem',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    display: 'block',
    marginBottom: '8px'
  },
  statusDisplay: {
    fontSize: '2rem',
    fontWeight: 800,
    letterSpacing: '0.02em'
  },
  scoreDisplay: {
    fontSize: '2rem',
    fontWeight: 800,
    color: '#ffffff'
  },
  timeDisplay: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#e2e8f0',
    marginTop: '10px'
  },
  sectionTitle: {
    fontSize: '1.4rem',
    fontWeight: 700,
    color: '#ffffff',
    marginBottom: '20px',
    borderLeft: '4px solid #3b82f6',
    paddingLeft: '12px'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px',
    marginBottom: '40px'
  },
  metricDetailCard: {
    backgroundColor: '#1e293b',
    borderRadius: '16px',
    border: '1px solid #334155',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    transition: 'all 0.3s ease'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottom: '1px solid #334155',
    paddingBottom: '12px',
    marginBottom: '8px'
  },
  statusBadge: {
    fontSize: '0.75rem',
    fontWeight: 700,
    padding: '4px 8px',
    borderRadius: '6px',
  },
  detailRow: {
    margin: 0,
    fontSize: '0.95rem',
    color: '#cbd5e1',
    lineHeight: '1.4'
  },
  code: {
    fontFamily: 'Consolas, monospace',
    backgroundColor: '#0f172a',
    padding: '2px 6px',
    borderRadius: '4px',
    color: '#60a5fa'
  },
  linkText: {
    color: '#3b82f6',
    textDecoration: 'underline',
    cursor: 'pointer'
  },
  financialImpactBox: {
    marginTop: 'auto',
    paddingTop: '16px',
    borderTop: '1px solid #334155',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  mitigationBox: {
    backgroundColor: '#0f172a',
    border: '1px solid #1e293b',
    borderRadius: '16px',
    padding: '30px',
    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)'
  },
  mitigationList: {
    margin: 0,
    paddingLeft: '20px',
    color: '#9ca3af'
  },
  mitigationItem: {
    marginBottom: '10px',
    lineHeight: '1.6'
  },
  placeholderBox: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#6b7280',
    fontSize: '1.1rem',
    border: '2px dashed #374151',
    borderRadius: '16px'
  }
};

// Glitch and pulsing CSS injection definitions
const glitchStyles = `
  @keyframes glitch {
    0% { transform: translate(0) }
    20% { transform: translate(-2px, 2px) }
    40% { transform: translate(-2px, -2px) }
    60% { transform: translate(2px, 2px) }
    80% { transform: translate(2px, -2px) }
    100% { transform: translate(0) }
  }
  .glitch-card {
    border: 2px solid #ff0055 !important;
    animation: glitch 0.25s infinite;
    position: relative;
    background-color: rgba(255, 0, 85, 0.05) !important;
  }
  .glitch-text {
    text-shadow: 1px 1px 0px #ff00c1, -1px -1px 0px #00fff0;
  }
  .neon-border {
    border: 2px solid #ff0055 !important;
    box-shadow: 0 0 15px rgba(255, 0, 85, 0.8), inset 0 0 15px rgba(255, 0, 85, 0.4) !important;
    animation: pulse 1.5s infinite alternate;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 5px rgba(255, 0, 85, 0.5) }
    100% { box-shadow: 0 0 25px rgba(255, 0, 85, 1) }
  }
`;

export default AuthorityDashboardComponent;