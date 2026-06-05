import React, { useState } from 'react';
import { AuthorityMeterProps } from './AuthorityMeter'; // Assume this component exists
import { ComplianceRiskData } from '../types/ComplianceTypes';

// State Machine 정의
type SystemState = 'INITIAL' | 'ANALYZING' | 'WARNING' | 'RESOLUTION' | 'SUCCESS';

interface AuthoritySimulatorProps {
    initialData: ComplianceRiskData[]; // 리서처가 제공한 데이터셋을 받음
}

const AuthoritySimulator: React.FC<AuthoritySimulatorProps> = ({ initialData }) => {
    const [state, setState] = useState<SystemState>('INITIAL');
    const [riskScore, setRiskScore] = useState(100);
    const [warningMessage, setWarningMessage] = useState('');

    // 💡 핵심 로직: 데이터 입력 -> 리스크 식별 (The Triad)
    const handleAnalyze = async () => {
        setState('ANALYZING');
        setWarningMessage('');

        // Mock API Call 시뮬레이션 (네트워크 지연 및 분석 과정 강조)
        await new Promise(resolve => setTimeout(resolve, 1500));

        // 1. 데이터 파싱 및 리스크 식별 로직 실행 (가상의 백엔드 호출)
        const detectedRisks = initialData.filter(data => data['L_reg'] > 0);
        if (detectedRisks.length === 0) {
            setRiskScore(100);
            setState('SUCCESS');
            setWarningMessage("✅ 모든 데이터가 시스템 표준 범위 내에 있습니다. 통제권 확보 완료.");
            return;
        }

        // 리스크 점수 계산 (L_reg 위반이 많을수록 낮은 점수)
        const totalRisk = detectedRisks.reduce((sum, risk) => sum + parseFloat(risk['Worst-Case L'].replace(/[$,]/g, '')), 0);
        const newScore = Math.max(10, 100 - (totalRisk / 25)); // 점수가 너무 낮아지지 않도록 최소값 보장

        setRiskScore(newScore);
        setState('WARNING');
        setWarningMessage(`⚠️ 시스템 경고: ${detectedRisks.length}개의 핵심 리스크를 발견했습니다. 총 위험 예측 손실액: $${totalRisk.toLocaleString()}.`);

    };

    // 2. 시스템적 통제권 확보 로직 실행 (Recovery Path)
    const handleResolve = async () => {
        setState('RESOLUTION');
        setWarningMessage("⚙️ 시스템이 데이터 무결성 검사를 시작합니다... 권위 재확립 중...");
        await new Promise(resolve => setTimeout(resolve, 2000)); // 강제 지연 효과

        // 통제권 확보 성공 시점의 로직 (예: 추가 인증 필요)
        const resolutionSuccess = window.confirm("시스템이 통제권을 재확립했습니다. 이 상황을 해결할 근거 자료를 입력하시겠습니까?");
        if (resolutionSuccess) {
            setRiskScore(95); // 임시적으로 점수를 회복했다고 가정
            setState('SUCCESS');
            setWarningMessage("✅ 권위적 통제권 확보 성공: 규정 및 데이터 기반의 해결책을 제시했습니다.");
        } else {
            setState('ANALYZING'); // 실패 시 다시 분석 상태로 돌아가도록 유도
            setWarningMessage("❌ 통제권 재확립에 실패했습니다. 추가적인 외부 검증이 필요합니다.");
        }
    };

    // UI 렌더링 로직 (상태 기계 기반)
    const renderContent = () => {
        switch (state) {
            case 'INITIAL':
                return (
                    <div>
                        <p className="text-lg mb-4">분석할 $L_{reg}$ 데이터셋을 확인했습니다. 3단계 시퀀스를 시작하려면 분석 버튼을 누르세요.</p>
                        <button onClick={handleAnalyze} disabled={!initialData || initialData.length === 0} className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition">
                            1단계: 데이터 분석 및 리스크 식별 시작 ➡️
                        </button>
                    </div>
                );
            case 'ANALYZING':
            case 'RESOLUTION':
                return (
                    <div className="flex flex-col items-center justify-center p-8 bg-yellow-100 border-l-4 border-yellow-500">
                        {state === 'ANALYZING' ? (
                            <>
                                <span className="text-xl font-bold text-red-600 mb-2">🔍 데이터 무결성 검사 중...</span>
                                <p>시스템이 $L_{reg}$ 데이터를 파싱하고, 잠재적 규정 위반 지점을 계산하는 중입니다. (지연 시간 1초 강제 적용)</p>
                            </>
                        ) : (
                            <span className="text-xl font-bold text-blue-600 mb-2">⚙️ 통제권 재확립 프로세스 시작...</span>
                        )}
                        <div className="spinner"></div> {/* 로딩 스피너 대체 */}
                    </div>
                );
            case 'WARNING':
                return (
                    <div className="bg-red-100 border-l-4 border-red-600 p-4 mb-4">
                        <h3 className="text-lg font-bold text-red-800 flex items-center"><span role="img" aria-label="경고">🚨</span> 시스템 경고: 통제권 공백(Compliance Gap) 감지</h3>
                        <p className="mt-1 text-sm">{warningMessage}</p>
                        <button onClick={handleResolve} className="mt-4 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded transition">
                            2단계: 시스템적 통제권 확보 시도 🔄
                        </button>
                    </div>
                );
            case 'SUCCESS':
                return (
                    <div className="bg-green-100 border-l-4 border-green-600 p-4 mb-4">
                        <h3 className="text-lg font-bold text-green-800 flex items-center"><span role="img" aria-label="성공">✅</span> 시스템 안정화 및 통제권 확보 완료</h3>
                        <p className="mt-1 text-sm">{warningMessage}</p>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="p-6 border rounded shadow-xl bg-white">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Authority Simulator v1.0</h2>
            <div className={`p-3 rounded ${state === 'WARNING' ? 'bg-red-50 border border-red-200' : state === 'SUCCESS' ? 'bg-green-50 border border-green-200' : ''} mb-4`}>
                <strong>[Authority Meter]</strong> 현재 통제 안정성 점수: <span className="text-3xl font-extrabold text-red-600">{riskScore.toFixed(1)}%</span>
            </div>

            {/* ⚠️ 실패/경고 메시지 표시 */}
            {renderContent()}
        </div>
    );
};

export default AuthoritySimulator;