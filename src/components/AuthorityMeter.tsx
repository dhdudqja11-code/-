import React from 'react';
import { useAuthority } from '../context/AuthorityProvider';
import { AuthorityState, LRegData } from '../types/authority-state';

// 컴포넌트 props 정의 (실제 사용 시 부모에서 데이터를 받도록 설계)
interface AuthorityMeterProps {
    initialLregData: LRegData; // 초기 진단 데이터셋을 받는다고 가정합니다.
}

/**
 * 시스템의 권위(Authority)를 시각적으로 보여주는 컴포넌트.
 * StateManager의 상태 변화에 따라 모든 애니메이션이 트리거됩니다.
 */
const AuthorityMeter: React.FC<AuthorityMeterProps> = ({ initialLregData }) => {
    // Context 훅을 사용하여 전역 상태를 구독합니다. (State Manager 종속)
    const { context, processLregData } = useAuthority();

    // 초기 로드 시, 제공된 데이터로 StateManager에 첫 입력을 강제 수행합니다.
    React.useEffect(() => {
        processLregData(initialLregData);
    }, [initialLregData, processLregData]);


    const getMeterColor = (state: AuthorityState): string => {
        switch (state) {
            case 'IDLE': return '#4A90E2'; // Blue/Default
            case 'ANALYZING': return '#FFC300'; // Amber/Yellow - 분석 중 경고성
            case 'WARNING': return '#D0021B'; // Red/Critical - 즉각적 위험 신호
            case 'CONTROLLED': return '#7ED321'; // Green/Safe - 통제권 확보 완료
        }
    };

    // --- [애니메이션 트리거 포인트 정의] ---
    const getGlitchClass = (state: AuthorityState): string => {
        if (state === 'WARNING') return 'glitch-active warning'; // Warning 시 Glitch 강도 최대로 설정
        if (state === 'ANALYZING') return 'glitch-subtle analyzing'; // 분석 중에는 미묘한 떨림만
        return 'glitch-none';
    };

    const handleSimulateDataUpdate = () => {
        // 시뮬레이션: 새로운 리스크 데이터를 강제로 주입하여 상태 전이 테스트
        console.log("--- [UI] 수동 데이터 업데이트 시도 ---");
        // 예시로, 더 심각한 리스크 데이터셋을 가정하고 재진행합니다.
        const newMockData: LRegData = { authorityScore: 45, lRegEstimateUsd: 120000, violationCount: 3 };
        processLregData(newMockData);
    };

    return (
        <div className="authority-dashboard">
            <h1>Authority Meter Dashboard</h1>
            
            {/* [Neon Glitch 효과 적용 영역] */}
            <div className={`meter-container ${getGlitchClass(context.state)}`}>
                <span className="meter-value" style={{ color: getMeterColor(context.state) }}>
                    {Math.round(context.authorityScore || 0)}%
                </span>
                <div className="meter-bar" style={{ backgroundColor: getMeterColor(context.state) }}></div>
            </div>

            {/* [Authority Meter 상태 표시 및 경고 애니메이션 영역] */}
            <div className={`status-panel ${context.state === 'WARNING' ? 'warning-flash' : ''}`}>
                <h2>시스템 권위 상태</h2>
                <p>{context.message}</p>
            </div>

            {/* [Loss Estimate 강조 패널] */}
            {context.currentLossEstimateUsd && context.state !== 'CONTROLLED' && (
                 <div className="loss-estimate-panel">
                    <h3>💸 즉시 조치 필요 손실 추정</h3>
                    <p style={{ fontSize: '2em', color: '#D0021B' }}>${context.currentLossEstimateUsd.toLocaleString()} USD</p>
                </div>
            )}

            <button onClick={handleSimulateDataUpdate}>🔥 리스크 데이터 재진입 (State Transition Test)</button>
        </div>
    );
};

export default AuthorityMeter;