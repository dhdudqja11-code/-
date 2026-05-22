// ... [생략] ...
/**
 * @description 백엔드 API 호출을 시뮬레이션하고, 리스크 점수를 계산하여 UI를 업데이트합니다.
 * Critical State 진입 시 애니메이션과 경고 메시지를 강제 출력합니다.
 */
const calculateRiskAndDisplayAlert = async (latestInput: string) => {
    // 1. Loading state management
    setIsLoading(true);
    setAlertMessage(null);
    
    try {
        // [실제로는 API Gateway를 통한 호출이 발생합니다]
        // Mocking the asynchronous API call for now
        await new Promise(resolve => setTimeout(resolve, 1000));

        const mockApiData = await fetchRiskScoreFromAPI({ latestInput }); // Replace with actual axios/fetch call
        
        // 2. Data validation and state update based on received data
        if (mockApiData?.riskLevel === 'Critical') {
            setRiskScore(Math.max(80, mockApiData.score));
            setAlertMessage(`🚨 경고: ${mockApiData.issueDescription} - 즉각적인 법적 대응이 필요합니다.`);
            // Critical State Trigger Logic
            triggerCriticalStateVisuals(); 
        } else {
            setRiskScore(Math.min(30, mockApiData.score));
            setAlertMessage(`✅ 현재 리스크 수준은 관리 가능 범위입니다. (${mockApiData.riskLevel})`);
            // Normal State Trigger Logic
            resetCriticalStateVisuals(); 
        }

    } catch (error) {
        console.error("Risk calculation failed:", error);
        setAlertMessage("❌ 시스템 오류: 리스크 계산에 실패했습니다. 잠시 후 다시 시도해주세요.");
        setRiskScore(0);
    } finally {
        setIsLoading(false);
    }
};

// Critical State Triggering Functions (These need implementation in the component body)
const triggerCriticalStateVisuals = () => {
    // 1. Global state/context to control parent container's class name (e.g., 'critical-bg')
    setIsInCriticalState(true);
};

const resetCriticalStateVisuals = () => {
    setIsInCriticalState(false);
};

// Mock API function for development purposes
const fetchRiskScoreFromAPI = async ({ latestInput: input }: { latestInput: string }) => {
    if (input.length < 5) return { score: 10, riskLevel: 'Low', issueDescription: 'N/A' };
    // Mock logic: if the input contains "violation", force Critical State
    if (input.toLowerCase().includes("violation")) {
        return { score: Math.floor(Math.random() * 40) + 70, riskLevel: 'Critical', issueDescription: `규정 위반 패턴 감지 (${new Date().toLocaleDateString()})` };
    } else if (input.length > 20 && input.includes("financial")) {
        return { score: Math.floor(Math.random() * 30) + 40, riskLevel: 'High', issueDescription: '재무 리스크 증가 추이' };
    } else {
        return { score: Math.floor(Math.random() * 20) + 10, riskLevel: 'Low', issueDescription: '안정적 상태 유지' };
    }
};

// ... [나머지 컴포넌트 코드는 변경 없음] ...