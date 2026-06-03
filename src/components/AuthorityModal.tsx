// src/components/AuthorityModal.tsx

import React, { useState, useCallback } from 'react';
import './AuthorityModal.css'; // 스타일 시트는 별도로 관리한다고 가정합니다.

/**
 * -----------------------------------------------------
 * [TYPE DEFINITION] 데이터 스키마 정의 (Researcher Dependency)
 * 이 인터페이스는 Researcher가 제공할 JSON 구조를 기반으로 합니다.
 * -----------------------------------------------------
 */

// 규제 위반 개별 항목의 상세 정보
export interface RegulatoryViolation {
  violationName: string; // 예: GDPR, CCPA 등 법규명
  riskLevel: 'High' | 'Medium' | 'Low'; // 리스크 수준
  financialImpactEstimateM$: number; // 추정 재무 피해액 (백만 달러)
  descriptionSnippet: string; // 위반 사례 요약 설명
}

// 전체 모달이 받을 데이터 구조
export interface AuthorityDataSchema {
  title: string; // 메인 헤드라인
  subCopy: string; // 서브 카피 (불안감 조성용)
  selectedCategory: string; // 사용자가 선택한 법규 카테고리
  violations: RegulatoryViolation[]; // 위반 사례 배열
}

/**
 * -----------------------------------------------------
 * [API MOCKUP] API 호출 지점 정의 (Future Integration Point)
 * 실제로는 서버 함수(Server Action/API Route)를 통해 데이터를 가져와야 합니다.
 * -----------------------------------------------------
 */

// Mocking: 실제로 외부 API를 호출하는 대신, 더미 로직을 사용합니다.
const fetchAuthorityData = async (category: string): Promise<AuthorityDataSchema> => {
  console.log(`[API CALL MOCK] Fetching data for category: ${category}...`);
  await new Promise(resolve => setTimeout(resolve, 800)); // 네트워크 지연 시뮬레이션

  // [TODO]: 여기에 실제 /api/authority-check 엔드포인트를 호출하는 로직을 작성해야 합니다.
  // 예시: const response = await fetch('/api/authority-check', { method: 'POST', body: JSON.stringify({ category }) });
  // return (await response.json()) as AuthorityDataSchema;

  return {
    title: "당신의 비즈니스, 혹시 다음 규제 변화에 취약하지 않으신가요?",
    subCopy: "현행 운영 데이터만으로는 예측할 수 없는, 미래의 법적 리스크가 존재합니다. 이 '정보의 공백'을 확인해야 합니다.",
    selectedCategory: category,
    violations: [
      { 
        violationName: "GDPR (유럽 일반 개인 정보 보호 규정)", 
        riskLevel: 'High', 
        financialImpactEstimateM$: 12.5, 
        descriptionSnippet: "사용자 동의 미확보 데이터 처리로 인한 벌금 및 소송 리스크." 
      },
      { 
        violationName: "CCPA (캘리포니아 소비자 개인정보법)", 
        riskLevel: 'Medium', 
        financialImpactEstimateM$: 4.2, 
        descriptionSnippet: "미국 거주자 데이터에 대한 투명성 및 삭제 요청 처리 미흡." 
      },
    ],
  };
};

/**
 * -----------------------------------------------------
 * [COMPONENTS] AuthorityModal Component (Main Render Logic)
 * @param initialData - 초기 로딩 시 사용할 더미 또는 실제 데이터.
 */
const AuthorityModal: React.FC<{ onCategoryChange: (category: string) => void }> = ({ onCategoryChange }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState<AuthorityDataSchema | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('GDPR');

  // 초기 로드 시 데이터 패칭
  React.useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        // 💡 API 통합 지점: 최초 데이터를 불러옵니다.
        const fetchedData = await fetchAuthorityData(selectedCategory);
        setData(fetchedData);
      } catch (error) {
        console.error("Failed to load authority data:", error);
        setData(null); // 에러 발생 시 null 처리
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [selectedCategory]);


  // 카테고리 변경 핸들러 (사용자 인터랙션)
  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category);
    onCategoryChange(category); // 부모 컴포넌트에 상태 변화 알림
  }, [onCategoryChange]);

  // ----------------- 1. 핵심 UI/UX 구조화 -----------------

  if (isLoading) {
    return <div className="modal-overlay">⚙️ 시스템 진단 중... 데이터를 로드하고 권위를 확보하는 중입니다.</div>;
  }

  if (!data) {
    return <div className="modal-overlay error">⚠️ 데이터 처리 오류: 리스크 정보를 불러올 수 없습니다. 관리자에게 문의하세요.</div>;
  }


  // ----------------- 2. Sub-Components (SRP 준수) -----------------

  const renderProblemStatement = () => (
    <div className="section problem-statement">
      <h1 className="modal-title">{data.title}</h1>
      <p className="sub-copy">{data.subCopy}</p>
      
      {/* 법규 카테고리 선택기 */}
      <div className="category-selector">
        <label htmlFor="authority-category">🔍 리스크 진단 기준:</label>
        <select 
          id="authority-category" 
          value={selectedCategory} 
          onChange={(e) => handleCategoryChange(e.target.value)}
        >
          <option value="GDPR">🌍 GDPR (유럽 개인정보)</option>
          <option value="CCPA">🇺🇸 CCPA (캘리포니아 거주자 데이터)</option>
          {/* [TODO]: 향후 추가될 법규 카테고리를 여기에 추가합니다. */}
        </select>
      </div>
    </div>
  );

  const renderViolationList = () => (
    <div className="section violation-list">
      <h2>🚨 주요 시스템 권위 경고 목록 ({data.violations.length}건 발견)</h2>
      {data.violations.map((violation, index) => (
        <div key={index} className={`warning-card ${violation.riskLevel.toLowerCase()}`}>
          <span className={`risk-badge risk-${violation.riskLevel.toLowerCase()}`}>{violation.riskLevel}</span>
          <h3>{violation.violationName}</h3>
          <p>{violation.descriptionSnippet}</p>
          <div className="financial-impact">
            💰 추정 재무 피해액: {violation.financialImpactEstimateM$}.0M 달러 
            <span className="disclaimer">(법적 근거 기반 추정치)</span>
          </div>
        </div>
      ))}
    </div>
  );


  return (
    <div className="modal-container">
      {renderProblemStatement()}
      <hr />
      {/* 💡 핵심 데이터 파싱 및 시각화 영역 */}
      {renderViolationList()}

      {/* [TODO]: 최종 액션 버튼 그룹 - 시스템적 통제권 확보 CTA */}
      <div className="action-footer">
        <button disabled>진단 보고서 생성 (Premium)</button>
        <button className="primary-cta">시스템 점검 리포트 요청</button>
      </div>
    </div>
  );
};

export default AuthorityModal;