import React, { useState, useEffect, useRef } from 'react';
import styles from './TrustProofSection.module.css'; // CSS 모듈 사용 가정

// ----------------------------------
// Mocking Components / Utilities
// ----------------------------------

interface ValidationStepProps {
  stepName: string;
  description: string;
  statusMessage: React.ReactNode;
}

const ValidationStep: React.FC<ValidationStepProps> = ({ stepName, description, statusMessage }) => (
  <div className={`${styles.validationContainer} ${styles.card}`}>
    <h3>⚙️ {stepName}: 데이터 무결성 검사</h3>
    <p className={styles.description}>{description}</p>
    <div className={`status-box ${styles.successBox}`}>{statusMessage}</div>
  </div>
);

// ----------------------------------
// Core Component: Trust Proof Section
// ----------------------------------

/**
 * 기술적 무결성을 '확신'으로 변환하는 인터랙티브 섹션 컴포넌트입니다.
 * 사용자가 스크롤에 따라 단계별로 정보를 얻게 만듭니다 (Mock Interaction).
 */
const TrustProofSection: React.FC = () => {
  // 각 단계가 활성화되었는지 추적하는 상태 관리
  const [activeStep, setActiveStep] = useState(1);

  // Intersection Observer를 사용하여 스크롤 위치에 따라 activeStep을 변경합니다.
  useEffect(() => {
    const elementRef = useRef<HTMLElement>(null);
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          // 섹션이 뷰포트에 들어왔다면, 스크롤 진행률에 따라 단계 결정
          const scrollRatio = Math.min(1, entry.intersectionRatio);
          let newStep: number;

          if (scrollRatio < 0.3) {
            newStep = 1; // 초기 진입
          } else if (scrollRatio < 0.75) {
            newStep = 2; // 중간 스크롤 구간
          } else {
            newStep = 3; // 하단 도달 / 완료
          }
          setActiveStep(newStep);
        }
      },
      { threshold: [0, 0.3, 0.75, 1] } // 0%, 30%, 75%, 100% 지점에서 콜백 호출
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    } else {
        // 초기 로드 시 강제로 활성화 상태 설정
        setActiveStep(1);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, []);


  return (
    <section id="trust-proof" className={styles.container} ref={useRef<HTMLElement>(null)}>
      <h1>🔒 기술적 무결성 증명 (Trust Proof)</h1>
      <p className={styles.leadText}>우리의 시스템은 단순히 '보안을 갖췄다'고 말하지 않습니다. **절대 변할 수 없는 기록**으로 확신을 경험하게 합니다.</p>

      {/* Step 1: AuthGateway Validation */}
      <div style={{ opacity: activeStep === 1 ? 1 : 0.4, transform: activeStep === 1 ? 'translateY(0)' : 'translateY(20px)', transition: 'all 0.6s ease' }}>
        <ValidationStep
          stepName="AuthGateway"
          description={`사용자 인증 및 API 요청이 발생할 때마다, 권한과 유효성을 즉시 검증합니다. 임의 접근은 원천 차단됩니다.`}
          statusMessage={
            <span style={{ color: '#1A56DB', fontWeight: 'bold' }}>✅ [Mock] 토큰 무결성 및 RBAC 검증 완료</span>
          }
        />
      </div>

      {/* Step 2: Data Flow & Integrity Check */}
      <div style={{ opacity: activeStep === 2 ? 1 : 0.4, transform: activeStep === 2 ? 'translateY(0)' : 'translateY(20px)', transition: 'all 0.6s ease', marginTop: '50px' }}>
        <ValidationStep
          stepName="Data Integrity Layer"
          description={`데이터가 시스템 내를 흐르는 모든 순간(Write/Read)에 대한 감사 로깅이 이루어집니다. 데이터 변조 시도는 즉시 탐지됩니다.`}
          statusMessage={
            <span style={{ color: '#FF9800', fontWeight: 'bold' }}>⚠️ [Mock] 시스템 내부 트랜잭션 흐름 정상 감지</span>
          }
        />
      </div>

      {/* Step 3: Immutable Audit Log (핵심 컴포넌트) */}
      <div style={{ opacity: activeStep === 3 ? 1 : 0.4, transform: activeStep === 3 ? 'translateY(0)' : 'translateY(20px)', transition: 'all 0.6s ease', marginTop: '50px' }}>
        <h2>📜 불변 감사 로그 (Immutable Audit Log)</h2>
        <p>모든 행위는 암호학적으로 연결된 블록체인 원칙에 따라 기록됩니다. 이는 시스템의 **공식적 진실(Official Truth)**입니다.</p>
        {/* 실제 데이터를 표시하는 시각적 영역 */}
        <div className={`${styles.auditLogContainer} ${styles.logGrid}`}>
            <div className={styles.logEntry}>
                <strong>[{new Date().toISOString()}]</strong>: <span style={{ color: '#333' }}>[USER_A]</span> - 
                <em style={{ marginLeft: '10px' }}>계정 정보 조회 요청</em> (Success)
            </div>
             <div className={styles.logEntry}>
                <strong>[{new Date().toISOString()}]</strong>: <span style={{ color: '#CC3333' }}>[SYSTEM]</span> - 
                <em style={{ marginLeft: '10px' }}>비정상적인 API 호출 시도 감지</em> (Blocked)
            </div>
             <div className={styles.logEntry}>
                <strong>[{new Date().toISOString()}]</strong>: <span style={{ color: '#333' }}>[ADMIN]</span> - 
                <em style={{ marginLeft: '10px' }}>정책 수정 및 권한 재설정</em> (Success)
            </div>
        </div>
      </div>
    </section>
  );
};

export default TrustProofSection;
```

<create_file path="c:\Users\user\AI 기업 두뇌\내 작업들\components\TrustProofSection.module.css">
```css
/* CSS Module for styling consistency */
.container {
    padding: 80px 5%;
    text-align: center;
    background: #f9fbfd; /* Light, trustworthy background */
}

h1 {
    font-size: 2.5rem;
    color: #1A56DB; /* Trust Blue */
    margin-bottom: 10px;
}

.leadText {
    font-size: 1.2rem;
    color: #555;
    margin-bottom: 40px;
}

/* Validation Step Card Styling */
.card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
    margin-bottom: 40px;
    text-align: left;
}

h3 {
    color: #333;
    border-left: 4px solid #1A56DB;
    padding-left: 10px;
}

.description {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 20px;
}

/* Status Box */
.status-box {
    display: inline-block;
    padding: 15px 30px;
    border-radius: 8px;
    font-weight: bold;
    background-color: #e6f2ff; /* Light blue background for success */
    color: #1A56DB;
    border: 1px solid #c4d9fa;
}

/* Audit Log Styling (Step 3) */
.auditLogContainer {
    margin-top: 30px;
    padding: 20px;
    background-color: #1e1e1e; /* Dark, technical background */
    border-radius: 8px;
    text-align: left;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}

.logEntry {
    display: flex;
    font-size: 0.95rem;
    margin-bottom: 8px;
    padding: 5px 0;
    border-bottom: 1px dashed #333;
}
/* End of CSS Module */