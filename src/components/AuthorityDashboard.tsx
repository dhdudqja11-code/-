/* 
 * Authority Dashboard Component: E2E 시뮬레이션의 핵심 UI 뼈대 (React/TSX)
 * 모든 상태 전이와 컴포넌트 표시가 이 파일에서 관리되어야 합니다.
 */
import React, { useState, useEffect } from 'react';

// API 응답 타입 정의 (서버 스키마를 기반으로 강제)
type AuthorityResponse = any; // 임시로 Any 사용

interface DashboardProps {}

const StatusStyles = {
    INITIAL: "text-green-400 border-green-500",
    WARNING: "text-amber-400 border-amber-500",
    BREACHED: "text-red-600 border-red-700 animate-pulse", // 경고 애니메이션 추가
    RESOLVED: "text-blue-400 border-blue-500"
}

export const AuthorityDashboard: React.FC<DashboardProps> = () => {
    const [status, setStatus] = useState<string>("INITIAL");
    const [authorityScore, setAuthorityScore] = useState(100);
    const [lossEstimate, setLossEstimate] = useState<number | null>(null);
    const [message, setMessage] = useState("");
    const [isBreached, setIsBreached] = useState(false);

    // 🚨 핵심 로직: API 호출 시뮬레이션 (실제로는 fetch('/api/v1/check_authority', ...))
    const simulateApiCall = async (testCase: string) => {
        console.log(`\n--- Running Test Case: ${testCase} ---`);

        // 1초 지연을 시뮬레이션하여 사용자 경험(UX)에 반영
        await new Promise(resolve => setTimeout(resolve, 500)); 

        let mockResponse;
        if (testCase.includes("Breach")) {
            mockResponse = { status_code: "BREACHED", authority_score: 15.0, loss_estimate: 98000.0, problem_definition: "...", root_cause_analysis: "...", mitigation_suggestion: "..." };
        } else if (testCase.includes("Warning")) {
            mockResponse = { status_code: "WARNING", authority_score: 65.0, loss_estimate: 12500.0, problem_definition: "...", root_cause_analysis: "...", mitigation_suggestion: "..." };
        } else {
            mockResponse = { status_code: "RESOLVED", authority_score: 95.0, loss_estimate: null, problem_definition: "...", root_cause_analysis: "...", mitigation_suggestion: "..." };
        }

        // ★ 중요: 상태 전이 및 지연 시간 로직 재현
        setStatus(mockResponse.status_code);
        setAuthorityScore(mockResponse.authority_score);
        setLossEstimate(mockResponse.loss_estimate);
        setMessage(mockResponse.problem_definition);
        setIsBreached(mockResponse.status_code === "BREACHED");

        // 실제 환경에서는 여기서 fetch를 통해 백엔드에 요청을 보내고, 
        // 응답의 status_code와 delay 로직을 처리해야 합니다.
    };

    return (
        <div className="p-8 bg-gray-900 text-white min-h-screen">
            <h1 className="text-3xl font-bold mb-6 text-amber-400">🛡️ Authority System Diagnostic Dashboard</h1>
            
            {/* 3단계 상태 전이 경고 패널 */}
            <div className={`p-4 border-l-8 transition duration-500 ${StatusStyles[status]}`} style={{ animation: isBreached ? 'flashRed 1s infinite' : 'none' }}>
                <h2 className="text-xl font-semibold">Current Status: {status}</h2>
                <p>{message}</p>
            </div>

            {/* 핵심 지표 컴포넌트 */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Authority Meter (시각화) */}
                <div className="bg-gray-800 p-6 rounded-xl shadow-lg border-t-4" style={{ borderColor: status === "BREACHED" ? 'red' : '#FFC300' }}>
                    <h3 className="text-lg font-medium mb-2">Authority Meter</h3>
                    <div className={`flex items-center gap-3`}>
                        <span className="text-4xl font-extrabold text-amber-400">{authorityScore.toFixed(1)}</span>
                        <span className="text-gray-400">/ 100%</span>
                    </div>
                    {/* 게이지 시각화 로직 구현 필요 */}
                </div>

                {/* Loss Estimate (재무적 위험) */}
                <div className="bg-gray-800 p-6 rounded-xl shadow-lg border-t-4" style={{ borderColor: status === "BREACHED" ? 'red' : '#FFC300' }}>
                    <h3 className="text-lg font-medium mb-2">Estimated Financial Loss</h3>
                    <p className={`text-3xl font-bold ${lossEstimate !== null && lossEstimate > 0 ? 'text-red-500' : 'text-green-400'}`}>
                        ${lossEstimate !== null ? lossEstimate.toLocaleString() : 'N/A'}
                    </p>
                    <p className="text-sm text-gray-400">Impact calculation based on Authority Breach level.</p>
                </div>

                 {/* Utility Solver (해결책 제시) */}
                <div className="bg-gray-800 p-6 rounded-xl shadow-lg border-t-4" style={{ borderColor: '#3b82f6' }}>
                    <h3 className="text-lg font-medium mb-2">Mitigation Suggestion</h3>
                    <p className="text-sm text-gray-300 leading-relaxed">
                        {/* 실제 API에서 받은 해결책 제시 텍스트가 여기에 들어갑니다. */}
                        <span className='italic'>[API 데이터 기반으로 자동 주입]</span>
                    </p>
                </div>
            </div>

            {/* 테스트 실행 버튼 (E2E Test Trigger) */}
            <div className="mt-10 flex gap-4">
                <button onClick={() => simulateApiCall("Resolved_Test")} className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition">
                    ✅ 정상 상태 (Initial $\to$ Resolved) 테스트
                </button>
                <button onClick={() => simulateApiCall("Warning_Test")} className="px-6 py-3 bg-amber-600 hover:bg-amber-700 rounded-lg transition">
                    ⚠️ 경고 발생 (Authority Warning) 테스트
                </button>
                <button onClick={() => simulateApiCall("Breach_Test")} className="px-6 py-3 bg-red-800 hover:bg-red-900 rounded-lg transition animate-pulse">
                    🔥 위반 상태 (Compliance Breach - 1s Delay) 테스트
                </button>
            </div>

        </div>
    );
}