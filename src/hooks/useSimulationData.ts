import { useState, useCallback } from 'react';
import { SimulationResult, SimulationError, SimulationInputParams, SimulationHookState } from '../types/simulation';

// NOTE: 실제 환경에서는 Axios나 React Query를 사용해야 하지만, 로직 검증을 위해 fetch API를 활용합니다.
const SIMULATION_API_ENDPOINT = '/api/v1/simulate-roi'; 

/**
 * Mini ROI 시뮬레이션 데이터 패칭 및 유효성 검사 커스텀 훅 (핵심)
 * @returns {SimulationHookState} - 현재 상태(data, error, loading)를 포함합니다.
 */
export const useSimulationData = (): SimulationHookState => {
    const [state, setState] = useState<SimulationHookState>({
        data: null, 
        error: null, 
        isLoading: false, 
        params: { industry: 'AI Tech', marketSizeMillionsUSD: 500, regulatoryComplianceScore: 85 } // 초기값 설정
    });

    /**
     * API 호출을 담당하며, 에러 핸들링 및 데이터 유효성 검사를 포함합니다.
     */
    const runSimulation = useCallback(async (params: SimulationInputParams) => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        try {
            // 1. 네트워크 호출 시도
            const response = await fetch(SIMULATION_API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params),
            });

            if (!response.ok) {
                // 2. HTTP 상태 코드 에러 처리 (4xx, 5xx 등)
                const errorData = await response.json();
                throw new Error(`API 호출 실패 (${response.status}): ${errorData.message || '서버 응답 오류'}`);
            }

            const rawJson: any = await response.json();

            // 3. 데이터 유효성 검증 (가장 중요!)
            if (!rawJson?.riskGrade || typeof rawJson?.estimatedLossAmountUSD !== 'number') {
                throw new Error("API 응답 스키마 불일치: 필수 필드(riskGrade, estimatedLossAmountUSD) 누락 또는 타입 오류.");
            }

            // 4. 데이터 구조 재구성 및 반환 (안정성 확보)
            const result: SimulationResult = {
                riskGrade: rawJson.riskGrade as 'Low' | 'Medium' | 'High' | 'Critical',
                estimatedLossAmountUSD: Number(rawJson.estimatedLossAmountUSD);
                mitigationActionPlan: Array.isArray(rawJson.mitigationActionPlan) ? rawJson.mitigationActionPlan : [];
            };

            // 5. 성공적으로 데이터를 받아왔으므로 상태 업데이트
            setState({
                data: result,
                error: null,
                isLoading: false,
                params: params // 현재 입력값 저장
            });

        } catch (e) {
            // 6. 최종 예외 처리 (네트워크 오류, JSON 파싱 에러 등 모든 것 포괄)
            const errorMessage = e instanceof Error ? e.message : "알 수 없는 시뮬레이션 오류가 발생했습니다.";
            setState(prev => ({
                ...prev,
                error: { 
                    errorCode: 500, // 일반적인 서버 에러 코드 할당
                    message: `시뮬레이션 실패: ${errorMessage}. 입력 데이터를 확인하거나 관리자에게 문의하세요.`,
                    details: e instanceof Error ? { stack: e.stack } : {}
                }, 
                isLoading: false
            }));
        }
    }, []);

    // 초기 로딩 시 실행되는 함수가 필요하므로, useCallback으로 감싸고 외부에서 호출하도록 노출합니다.
    return { state, runSimulation };
};