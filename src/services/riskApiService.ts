/**
 * @fileoverview ComplianceRiskDashboard 컴포넌트가 사용할 규제 위험 데이터를 페칭하는 Mock 서비스 레이어.
 * E2E 테스트 환경에서 외부 API 의존성을 제거하고, 표준화된 JSON 응답을 시뮬레이션합니다.
 */

// --- 1. 데이터 타입 정의 (Strong Typing for TypeScript) ---
export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical';

/** 규제 위험 경고의 상세 구조 */
export interface ComplianceRiskAlert {
  level: RiskLevel; // Critical, High 등
  whatWentWrong: string; // [1] 문제 정의 (What went wrong?)
  whyDidItGoWrong: string; // [2] 원인 분석 (Why did it go wrong? Source/Time)
  howToFixIt: string; // [3] 해결책 제시 (How to fix it?)
}

/** 전체 규제 위험 데이터의 구조 */
export interface RiskData {
  timestamp: string;
  sourceSystem: string;
  alert: ComplianceRiskAlert;
  lossVisualizationValue: number; // 예상 손실액 수치화 값 (예: $1,234,567)
}

/** ------------------------------------------- */
 * @function fetchRiskData
 * 규제 위험 데이터를 비동기적으로 시뮬레이션하여 가져옵니다.
 * 실제 환경에서는 API Gateway 호출을 대체합니다.
 * @param {string} transactionId - 분석할 트랜잭션 ID (예시)
 * @returns {Promise<RiskData>} 구조화된 규제 위험 데이터 객체
 */
export const fetchRiskData = async (transactionId: string): Promise<RiskData> => {
  console.log(`[Mock API Call] Fetching risk data for Transaction ID: ${transactionId}...`);

  // 💡 실제 API 호출 시뮬레이션 delay
  await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));

  // --- Mocking Logic (테스트 데이터 반환) ---
  if (!transactionId || transactionId.length < 10) {
    return {
      timestamp: new Date().toISOString(),
      sourceSystem: 'MOCK_ERROR',
      alert: {
        level: 'Low',
        whatWentWrong: 'Invalid Transaction ID provided.',
        whyDidItGoWrong: 'Input validation failed. Please provide a unique, structured transaction identifier.',
        howToFixIt: 'Ensure the calling service sends an ID matching the required UUID format.',
      },
      lossVisualizationValue: 0,
    };
  }

  // Critical Risk 시나리오를 강제 반환하여 컴포넌트가 제대로 작동하는지 테스트 유도
  const mockData: RiskData = {
    timestamp: new Date().toISOString(),
    sourceSystem: 'GDPR_Compliance_Gateway', // 출처 명시 (Source)
    alert: {
      level: 'Critical', // 최고 위험 등급으로 설정하여 경고 극대화
      whatWentWrong: '개인 식별 정보(PII)의 비인가 전송 감지.', // 문제 정의
      whyDidItGoWrong: `API Gateway Log ${transactionId}에서, 규정 외 영역(${new Date().toLocaleDateString()})으로 PII가 유출될 징후 포착.`, // 원인 분석 (Source/Time)
      howToFixIt: '즉시 트랜잭션을 중단하고, 데이터 전송 경로는 반드시 암호화된 엔드포인트(HTTPS/TLS)를 사용해야 합니다.', // 해결책 제시
    },
    lossVisualizationValue: 1234567.89, // 구체적인 손실액 수치화
  };

  console.log(`[Mock API Success] Successfully retrieved risk data for ${transactionId}.`);
  return mockData;
};

/** Mocking Layer의 유효성을 검사하는 더미 함수 */
export const checkRiskApiStatus = (): boolean => {
    // 실제로는 /healthcheck 등의 엔드포인트를 호출합니다.
    console.log("✅ API Gateway Health Check: Operational.");
    return true;
};