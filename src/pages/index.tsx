import React, { useState, useEffect } from 'react';
import RiskGauge from '../components/RiskGauge';
import { AuditBlock, ALVData, MiniRocianState } from '../types/miniRocianTypes';

// ==============================
// ⚠️ MOCK API Simulation Function
// 실제 환경에서는 이 부분이 axios.get('/api/v1/audit-gate') 와 같은 호출로 대체됩니다.
const fetchAuditDataMock = (): Promise<{ auditBlock: AuditBlock, alvData: ALVData }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 테스트를 위해 Critical 상태의 데이터를 강제 주입합니다.
      const criticalData: AuditBlock = {
        transactionId: 'TX-928374ABC',
        timestamp: new Date(),
        riskScore: 0.95, // 95%
        riskLevel: 'CRITICAL', // Critical 강제 설정
        problemDefinition: '데이터 출처(Source) 불명확성으로 인한 법적 증거력 상실 위험.',
        rootCauseAnalysis: '전통적인 트랜잭션 로그만으로는 규제 기관의 감사 요구사항을 충족할 수 없습니다. (Missing Source/Time)',
        mitigationSuggestion: '불변 감사 게이트웨이(IAG)를 통해 모든 트랜잭션을 처리하고, 체이닝 해싱 기반의 AuditBlock을 필수적으로 생성해야 합니다.',
      };

      const alvDataMock: ALVData = {
          estimatedLossAmountUSD: 3250000.00, // $3.25M
          impactScore: 98,
          mitigationRequiredYears: 2,
      };

      resolve({ auditBlock: criticalData, alvData: alvDataMock });
    }, 1500); // 로딩 지연 시뮬레이션
  });
};
// ==============================


// [1] ALV Card Component (재무적 손실액 시각화)
const ALVCard: React.FC<{ data: ALVData }> = ({ data }) => (
    <div style={{ padding: '20px', borderLeft: '4px solid #e74c3c', backgroundColor: '#fdeded' }}>
        <h4>💰 추정 재무 손실액 (ALV)</h4>
        <p style={{ fontSize: '2.5em', color: '#e74c3c', margin: '10px 0' }}>
            ${data.estimatedLossAmountUSD.toLocaleString()} <span style={{ fontSize: '0.6em' }}>(미화)</span>
        </p>
        <small>영향도 점수: {data.impactScore}% | 완화 필요 기간: {data.mitigationRequiredYears}년</small>
    </div>
);

// [2] Legal Block Component (법적/감사 증명력 제공)
const LegalBlock: React.FC<{ auditData: AuditBlock }> = ({ auditData }) => (
    <div style={{ padding: '15px', border: '1px dashed #aaa', backgroundColor: '#f7f7ff' }}>
        <h5>📜 감사 로그 및 법적 근거 제시</h5>
        <p><strong>[문제 정의]</strong> {auditData.problemDefinition}</p>
        <hr/>
        <p style={{ fontSize: '0.9em', color: '#666' }}>
            <strong>원인 분석 (Source/Time):</strong> {auditData.rootCauseAnalysis} <br/>
            (Immutable Proof, Source:{'IAG'}, Time:{new Date().toISOString()}) 🛡️
        </p>
        <p style={{ fontWeight: 'bold', marginTop: '10px' }}>
            ✅ [해결책 제시] {auditData.mitigationSuggestion}
        </p>
    </div>
);


// ==============================
// 메인 대시보드 컴포넌트 (상태 관리 및 흐름 제어)
const MiniRocianDashboard: React.FC = () => {
  const [state, setState] = useState<MiniRocianState>({ isLoading: true });

  useEffect(() => {
    // 데이터 로딩 시뮬레이션 시작
    fetchAuditDataMock()
      .then(({ auditBlock, alvData }) => {
        setState({ 
            auditBlock: auditBlock, 
            alvData: alvData, 
            isLoading: false, 
            hasCriticalAlert: auditBlock.riskLevel === 'CRITICAL' 
        });
      })
      .catch(error => {
        console.error("Failed to fetch data:", error);
        setState({ isLoading: false });
      });
  }, []);

  const handleModalClose = () => {
    // 모달에서만 처리되는 로직 (예: 사용자에게 보고서 요청)
    alert("⚠️ 경고: 위험도가 Critical 레벨로 감지되었습니다. 시스템이 자동으로 보호 조치(Mitigation Suggestion)를 제시합니다.");
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '40px' }}>
      <h1>🔬 Mini ROI 리스크 시뮬레이션 대시보드</h1>
      <p>데이터 흐름: 위험 감지 $\rightarrow$ 손실 추정 $\rightarrow$ 완화 필요성</p>

      {/* 🚨 Critical Modal 강제 노출 로직 */}
      {(state.hasCriticalAlert && !state.isLoading) && (
        <div style={{ 
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
            backgroundColor: 'rgba(217, 83, 79, 0.8)', zIndex: 1000, 
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{ background: 'white', padding: '40px', borderRadius: '12px', maxWidth: '600px', textAlign: 'center', boxShadow: '0 5px 15px rgba(0,0,0,0.3)' }}>
            <h2>🚨 [SYSTEM ALERT] Critical Security Threat Detected!</h2>
            <p style={{ color: '#d9534f', fontSize: '1.2em' }}>
                시스템이 현재 트랜잭션의 위험도를 **Critical** 레벨로 진단했습니다. 즉시 다음 조치를 취해야 합니다.
            </p>
            <button 
                onClick={handleModalClose} 
                style={{ padding: '10px 20px', background: '#d9534f', color: 'white', border: 'none', cursor: 'pointer' }}
            >
                위험 경고 확인 및 상세 분석 보기 →
            </button>
          </div>
        </div>
      )}

      {/* 데이터 로딩 상태 */}
      {!state.isLoading && state.auditBlock && (
        <div style={{ display: 'grid', grid-template-columns: 1fr; gap: '20px' }}>
            
            {/* [1] RiskGauge (가장 위에 위치하여 즉각적인 위험 인지 유도) */}
            <RiskGauge auditData={state.auditBlock} />

            <div style={{ display: 'grid', grid-template-columns: 1fr; gap: '20px' }}>
                {/* [2] ALV Card (재무적 손실액 시각화) */}
                <ALVCard data={state.alvData || { estimatedLossAmountUSD: 0, impactScore: 0, mitigationRequiredYears: 0 }} />

                {/* [3] Legal Block (법적 근거 제시 - 왜 위험한지 설명) */}
                <LegalBlock auditData={state.auditBlock} />
            </div>
        </div>
      )}

    </div>
  );
};

export default MiniRocianDashboard;