import React from 'react';
import { AuditBlock, RiskLevel } from '../types/miniRocianTypes';

interface RiskGaugeProps {
  auditData: AuditBlock;
}

const getRiskStyles = (level: RiskLevel) => {
  switch (level) {
    case 'CRITICAL':
      return { color: '#d9534f', label: '🚨 Critical Alert' }; // Red
    case 'HIGH':
      return { color: '#f0ad4e', label: '⚠️ High Risk' };     // Orange
    case 'MEDIUM':
      return { color: '#5bc0de', label: '🟡 Medium Concern' };  // Blue/Yellow
    case 'LOW':
    default:
      return { color: '#5cb85c', label: '✅ Low Risk' };        // Green
  }
};

const RiskGauge: React.FC<RiskGaugeProps> = ({ auditData }) => {
  const styles = getRiskStyles(auditData.riskLevel);

  return (
    <div style={{ 
      padding: '20px', 
      border: '1px solid #ccc', 
      borderRadius: '8px', 
      backgroundColor: '#f9f9f9' 
    }}>
      <h3>🛡️ 시스템 위험 레벨 게이지</h3>
      <div style={{ textAlign: 'center', margin: '20px 0' }}>
        {/* 시각적 게이지 표현 (Mock) */}
        <div 
          style={{ 
            width: '80%', 
            height: '30px', 
            backgroundColor: '#eee', 
            borderRadius: '15px', 
            overflow: 'hidden' 
          }}
        >
          <div 
            style={{ 
              width: `${(auditData.riskScore * 100).toFixed(0)}%`, 
              height: '100%', 
              backgroundColor: styles.color, 
              transition: 'width 0.5s ease' 
            }}
          ></div>
        </div>
      </div>
      <div style={{ textAlign: 'center', fontSize: '2em', color: styles.color }}>
        {styles.label}
      </div>
      <p style={{ marginTop: '10px', fontSize: '0.9em' }}>
        Risk Score: <span style={{ fontWeight: 'bold' }}>{(auditData.riskScore * 100).toFixed(2)}%</span>
      </p>
    </div>
  );
};

export default RiskGauge;