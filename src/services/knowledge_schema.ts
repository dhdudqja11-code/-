/**
 * @file KnowledgeService Core Schema Definition (Source of Truth)
 * 
 * 이 파일은 '마음을 묻다' 서비스의 모든 핵심 개념(Ontology)이 가져야 할 구조를 정의합니다.
 * Writer가 작성한 콘텐츠는 반드시 이 스키마를 따르도록 강제해야 합니다.
 */

/**
 * CoreConceptSchema: 시스템에 등록될 단일 핵심 개념의 표준 구조.
 * @param conceptName - 고유 식별자 (예: "불확실성 제거 권한")
 * @param definitionText - 학술적/철학적으로 가장 정확한 정의 문장. (필수)
 * @param sourceReference - 이 정의가 나온 근본적인 출처 (ex: Cognitive Bias Theory, GDPR Art. 17). (필수)
 * @param requiredComponents - 이 개념을 표현하기 위해 필요한 시스템 컴포넌트 목록 (예: 'AuditLogComponent', 'API_Gateway').
 * @param useCaseGuideline - 콘텐츠/마케팅에서 사용해야 하는 명확한 가이드라인.
 */
export interface CoreConceptSchema {
    conceptName: string; 
    definitionText: string; 
    sourceReference: string; 
    requiredComponents: string[];
    useCaseGuideline: string;
}

/**
 * KnowledgeService API Input Schema (Validation용)
 * 외부에서 지식 정의를 주입할 때 사용되는 데이터 모델.
 */
export interface IngestionPayload {
    conceptName: string;
    definitionText: string;
    sourceReference: string; 
    useCaseGuideline: string;
    // 임시적으로 필수 컴포넌트 목록은 API 게이트웨이 레벨에서 결정한다고 가정합니다.
}

/**
 * 시스템의 모든 핵심 개념을 담는 글로벌 캐시 (실제로는 DB 접근)
 */
export type KnowledgeStore = Record<string, CoreConceptSchema>;

// 초기 빈 스토어 정의. 실제 데이터는 Writer가 주입할 예정입니다.
export const initialKnowledgeStore: KnowledgeStore = {};

/**
 * [Self-Correction Notice] 
 * 이 스키마를 기반으로 모든 에이전트의 산출물 검증 로직을 작성해야 합니다.
 */