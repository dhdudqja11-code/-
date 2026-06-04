// src/components/AuthorityDashboardComponent.tsx
import React, { useState } from 'react';

/**
 * @typedef {Object} LegalRiskData
 * @property {string} source - 리스크 데이터의 출처 (예: GDPR-2018)
 * @property {number} severityScore - 심각도 점수 (0.0 ~ 1.0)
 * @property {string} violationMechanism - 위반 메커니즘 설명
 * @property {Array<{field: string, value: any}>} potentialFailures - 잠재적 오류 필드 목록
 */

/**
 * 가상의 법률 리스크 데이터 타입 정의
 * 실제 구현 시 Researcher가 제공하는 JSON 스키마를 따름.
 */
interface LegalRiskProps {
  riskData: LegalRiskData;
  // 외부 API 호출 결과를 받을 상태 관리용 Props 추가 (더미)
  initialAuthorityStatus?: 'UNKNOWN' | 'SAFE' | 'WARNING'; 
}

/**
 * [Core Component] 법률 리스크 데이터를 시각화하고 권위적 경고를 출력하는 대시보드 스켈레톤.
 * 이 컴포넌트는 순수하게 UI/UX와 데이터 파싱 로직만 담당하며, 실제 API 호출은 'AuthorityCheckerService' 내부로 분리합니다.
 * @param {LegalRiskProps} props - 법률 리스크 데이터를 포함한 Props.
 */
const AuthorityDashboardComponent: React.FC<LegalRiskProps> = ({ 
  riskData, 
  initialAuthorityStatus = 'UNKNOWN' 
}) => {
  // [State Management] 시스템 상태를 관리하여 UI의 반응성을 높입니다.
  const [authorityMessage, setAuthorityMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  /**
   * 핵심 로직: API 호출 지점 시뮬레이션 및 Authority Warning 생성 (★가장 중요★)
   * 이 함수는 실제 백엔드 엔드포인트 (예: POST /api/v1/check_authority)를 호출하는 자리입니다.
   */
  const handleAuthorityCheck = async () => {
    if (!riskData || riskData.severityScore === undefined) {
      alert("🚨 경고: 검사할 법률 리스크 데이터가 없습니다. JSON 스키마를 확인하세요.");
      return;
    }

    setIsProcessing(true);
    setAuthorityMessage(null); 

    // [DUMMY API CALL SIMULATION]
    console.log(`[API Simulation]: Calling Authority Checker with risk score: ${riskData.severityScore}`);
    
    // 실제 환경에서는 fetch()를 사용하여 백엔드 엔드포인트에 요청을 보냅니다.
    await new Promise(resolve => setTimeout(resolve, 1500)); // 네트워크 지연 시뮬레이션

    try {
      // !!! 이 부분을 실제 API 호출로 대체해야 합니다. !!!
      const simulatedApiResponse = simulateAuthorityAPIResponse(riskData);
      
      setAuthorityMessage(simulatedApiResponse.message);
      console.log(`[Success] Authority Check Passed. Status: ${simulatedApiResponse.status}`);

    } catch (error) {
      // API 호출 실패 시, 시스템적 권위 유지 로직이 작동해야 합니다.
      setAuthorityMessage("⚠️ 통제권 재확립 중... 외부 연결 오류가 감지되었습니다. 잠시 후 다시 시도해 주십시오.");
      console.error("[Error] Authority Check Failed:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * 가상의 API 응답을 생성하는 더미 함수 (테스트용)
   * 이 로직은 실제 백엔드에서 복잡하게 처리되어야 할 핵심 비즈니스 로직의 역할을 수행합니다.
   */
  const simulateAuthorityAPIResponse = (data: LegalRiskData): { status: string; message: string } => {
    // 리스크 점수에 따라 경고 상태를 결정하는 가상의 백엔드 로직입니다.
    if (data.severityScore > 0.7) {
      return { 
        status: 'WARNING', 
        message: `🚨 [Authority Warning] ${data.source} 규정 위반 가능성이 높습니다. 원인 분석 및 즉각적인 해결책 제시가 필요합니다.` 
      };
    } else if (data.severityScore > 0.4) {
      return { status: 'NOTICE', message: `⚠️ [Notice] ${data.source} 관련 잠재적 리스크를 인지하고 모니터링이 필요합니다.` };
    } else {
      return { status: 'SAFE', message: `✅ 시스템 검증 완료. 현재까지의 리스크는 허용 가능한 범위 내에 있습니다. (Authority Confirmed)` };
    }
  };


  // --- 렌더링 로직 시작 ---

  return (
    <div style={styles.container}>
      <h2>🛡️ 규제 컴플라이언스 대시보드</h2>
      <p>데이터 파싱 및 시스템적 통제권 확보 현황을 실시간으로 확인하십시오.</p>

      {/* 1. 핵심 지표 섹션 (Researcher 데이터 표시) */}
      <div style={styles.metricGrid}>
        <MetricCard title="최고 리스크 점수" value={`${(riskData?.severityScore || 0).toFixed(2)}`} color={riskData?.severityScore > 0.7 ? '#e74c3c' : '#2ecc71'} />
        <MetricCard title="주요 위반 근거" value={riskData?.source || 'N/A'} />
        <MetricCard title="잠재적 실패 유형" value={`${riskData?.potentialFailures?.length || 0}개`} />
      </div>

      {/* 2. 권위 경고 및 검증 섹션 */}
      <div style={styles.warningBox}>
        <h3>🔗 실시간 Authority Check</h3>
        <button 
          onClick={handleAuthorityCheck} 
          disabled={isProcessing}
          style={styles.checkButton}
        >
          {isProcessing ? '검증 중...' : '시스템 권위 검사 실행'}
        </button>

        {/* [API 호출 결과 출력 영역] */}
        <div style={{ marginTop: '20px', borderLeft: '3px solid #f1c40f', paddingLeft: '15px' }}>
          <h4>📊 시스템 진단 보고서</h4>
          {authorityMessage ? (
            <p style={styles.resultText}>{authorityMessage}</p>
          ) : (
            <p style={{ color: '#7f8c8d' }}>버튼을 클릭하여 시스템적 권위 검사를 실행해 주십시오.</p>
          )}
        </div>

        {/* [핵심 API 호출 지점 표시] */}
        <div className="api-placeholder" style={styles.apiPlaceholder}>
            {/* 🎯 이 컴포넌트의 가장 중요한 목적입니다. 실제 백엔드(FastAPI/Django)에서 외부 리스크 데이터를 받아 처리하는 엔드포인트가 여기에 연결됩니다. */}
            <pre><code>// const apiResponse = await fetch('/api/v1/check_authority', { method: 'POST', body: JSON.stringify({ data }) });</code></pre>
        </div>

      </div>
    </div>
  );
};

// 재사용 가능한 하위 컴포넌트 (가정)
interface MetricCardProps { title: string; value: string; color?: string; }
const MetricCard: React.FC<MetricCardProps> = ({ title, value, color }) => (
    <div style={styles.metricCard}>
        <strong>{title}</strong>
        <p style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{value}</p>
    </div>
);

// 스타일 정의 (가독성을 위해 인라인 스타일 사용)
const styles: { [key: string]: React.CSSProperties } = {
  container: { fontFamily: 'Arial, sans-serif', maxWidth: '1000px', margin: '0 auto', padding: '20px' },
  metricGrid: { display: 'flex', gap: '20px', marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid #eee' },
  metricCard: { flex: 1, padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
  warningBox: { border: '1px solid #ddd', padding: '30px', borderRadius: '10px', backgroundColor: '#fef9e7' },
  checkButton: { 
    padding: '12px 25px', 
    fontSize: '1.1em', 
    cursor: 'pointer', 
    backgroundColor: '#3498db', 
    color: 'white', 
    border: 'none', 
    borderRadius: '5px', 
    transition: 'background-color 0.2s' 
  },
  resultText: { 
    fontSize: '1.1em', 
    fontWeight: 'bold', 
    padding: '10px', 
    backgroundColor: '#ecf0f1', 
    borderRadius: '5px',
    whiteSpace: 'pre-wrap' // 줄바꿈 유지
  },
  apiPlaceholder: {
      marginTop: '25px',
      padding: '20px',
      border: '2px dashed #bdc3b1',
      backgroundColor: '#f4f6f8',
      borderRadius: '8px'
  }
};

export default AuthorityDashboardComponent;