import React, { createContext, useContext, useState, useCallback } from 'react';
import { AuthorityState, LRegData, initialAuthorityContext, AuthorityContextValue } from '../types/authority-state';

// --- [핵심 비즈니스 로직: 상태 전이 및 Loss Estimate 처리] ---
/**
 * $L_{reg}$ 데이터를 기반으로 시스템의 권위(Authority) 상태를 계산합니다.
 * 이 함수가 StateManager의 핵심이며, 모든 외부 데이터는 반드시 이 필터를 거쳐야 합니다.
 * @param lRegData 입력 규제 리스크 데이터셋
 * @returns { AuthorityContextValue } 새로운 상태 값과 메시지
 */
const processAuthorityState = (lRegData: LRegData): AuthorityContextValue => {
    let newState: AuthorityState;
    let message: string;
    let lossEstimate: number | null;

    // 1. Loss Estimate 기반 경고 트리거 로직
    if (lRegData.lRegEstimateUsd > 0 && lRegData.authorityScore < 60) {
        lossEstimate = Math.round(lRegData.lRegEstimateUsd); // USD를 정수로 반올림
        newState = 'WARNING';
        // [근거: L_reg 데이터셋 스키마 정의] - 벌금액이 존재하고 점수가 낮으면 경고 상태 진입
        message = `[🚨 경고] 규제 리스크 감지. 예상 손실 규모: $${lossEstimate} USD. 통제권 확보가 시급합니다.`;
    } 
    // 2. Warning State에서 Controlled로의 전이 (임시 로직)
    else if (lRegData.authorityScore >= 90 && lRegData.violationCount === 0) {
        lossEstimate = 0;
        newState = 'CONTROLLED';
        message = `[✅ 통제 성공] 시스템적 권위 확보 완료. 현재 규제 리스크는 안정권에 있습니다.`;
    } 
    // 3. 초기 또는 분석 중 상태
    else {
        lossEstimate = lRegData.lRegEstimateUsd;
        newState = 'ANALYZING';
        message = `[🔄 분석 중] $L_{reg}$ 데이터를 검증하는 중입니다. Authority Score: ${Math.round(lRegData.authorityScore)} / 100`;
    }

    return {
        state: newState,
        currentLossEstimateUsd: lossEstimate,
        message: message,
    };
};


// --- [React Context Provider] ---
export const AuthorityContext = createContext<AuthorityContextValue>(initialAuthorityContext);

interface AuthorityProviderProps {}

/**
 * Authority Meter의 상태 전이를 관리하는 메인 Provider 컴포넌트.
 */
export const AuthorityProvider: React.FC<AuthorityProviderProps> = ({ children }) => {
    const [context, setContext] = useState<AuthorityContextValue>(initialAuthorityContext);

    // LRegData를 입력받아 StateManager 로직을 실행하는 함수 (핵심 API)
    const processLregData = useCallback((lRegData: LRegData) => {
        console.log('--- [StateManager] Authority Process Start ---');
        const newContextValue = processAuthorityState(lRegData);

        // State가 변경될 때만 부모 컴포넌트에게 알림 (성능 최적화)
        setContext(newContextValue);
        console.log(`[StateManager] State Transition: ${newContextValue.state} -> ${processAuthorityState(lRegData).state}`);

    }, []); // 의존성 배열 비움 = 이 함수 자체는 변경되지 않음

    const value = {
        context,
        processLregData,
    };

    return (
        <AuthorityContext.Provider value={value}>
            {children}
        </AuthorityContext.Provider>
    );
};

/**
 * Context를 사용하는 커스텀 훅
 */
export const useAuthority = () => useContext(AuthorityContext);