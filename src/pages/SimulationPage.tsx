import React, { useState } from 'react';
import { useSimulationData } from '../hooks/useSimulationData';
import { SimulationInputParams } from '../types/simulation';

// 임시 스타일링 컴포넌트 (실제 프로젝트에서는 CSS 모듈 사용 권장)
const Card = ({ children }) => <div className="p-6 bg-white shadow-xl rounded-lg">{children}</div>;
const Button = ({ onClick, disabled, children }) => (
    <button 
        onClick={onClick} 
        disabled={disabled}
        className={`px-8 py-3 text-lg font-bold rounded transition duration-200 ${disabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white'}`}
    >
        {children}
    </button>
);

/**
 * 시뮬레이션 결과를 시각적으로 표현하는 컴포넌트 (Designer가 정의한 Critical UX 반영)
 */
const ResultDisplay = ({ result }) => {
    let colorClass = 'text-green-600 bg-green-100'; // 기본값
    if (result.riskGrade === 'Critical') {
        colorClass = 'text-red-700 bg-red-100 animate-pulse shadow-lg ring-4 ring-red-500/50'; // Critical 강조
    } else if (result.riskGrade === 'High') {
        colorClass = 'text-orange-700 bg-orange-100';
    }

    return (
        <div className="mt-8 p-12 border-4 border-dashed border-gray-200 rounded-xl">
            <h2 className={`text-3xl font-extrabold ${colorClass.includes('red') ? 'animate-pulse' : ''}`}>
                🚨 위험 등급 진단: {result.riskGrade} ({colorClass})
            </h2>
            <p className="mt-4 text-xl text-gray-600">
                현재 비즈니스 구조는 심각한 법적/규제 리스크에 직면해 있습니다. 즉각적인 대응이 필요합니다.
            </p>

            <div className="mt-8 grid grid-cols-2 gap-6">
                <div>
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">💰 추정 재무 손실액 (Loss)</h3>
                    <p className={`text-5xl font-black ${result.riskGrade === 'Critical' ? 'text-red-600 animate-pulse' : 'text-indigo-600'}`}>
                        ${result.estimatedLossAmountUSD.toLocaleString()} USD
                    </p>
                </div>
                <div>
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">✅ 검증된 데이터 출처</h3>
                    <p className="text-lg text-gray-500">{result.sourceDataVerification?.source || '정보 없음'}</p>
                </div>
            </div>

            <h3 className="mt-10 text-2xl font-bold border-b pb-2">💡 즉각적인 해결책 제시 (Action Plan)</h3>
            <ul className="list-disc pl-6 space-y-2 mt-4">
                {result.mitigationActionPlan.map((action, index) => (
                    <li key={index} className={`p-2 rounded ${result.riskGrade === 'Critical' ? 'bg-red-50 border-l-4 border-red-500' : 'border-l-4 border-indigo-300'}`}>
                        {action}
                    </li>
                ))}
            </ul>
        </div>
    );
};

/**
 * 메인 시뮬레이션 페이지 컴포넌트
 */
const SimulationPage: React.FC = () => {
    // useSimulationData 훅을 사용하여 로직과 상태를 분리합니다.
    const { state, runSimulation } = useSimulationData();
    const [params, setParams] = useState<SimulationInputParams>(state.params);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        let newValue: any = value;

        // 입력 필드에 따른 타입 캐스팅 로직 추가
        if (name === 'marketSizeMillionsUSD' || name === 'regulatoryComplianceScore') {
            newValue = parseFloat(value) || 0;
        }
        setParams({ ...params, [name]: newValue });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await runSimulation(params);
    };

    // --- 조건부 렌더링 로직 ---

    if (state.isLoading) {
        return <div className="text-center py-20"><h1 className="text-3xl font-bold">⚙️ 시뮬레이션 실행 중...</h1><p>최적의 위험 데이터를 분석하고 있습니다. 잠시만 기다려 주세요.</p></div>;
    }

    if (state.error) {
        return <div className="text-center py-20 bg-red-50 border border-red-300 rounded-xl p-10">
            <h1 className="text-4xl font-extrabold text-red-700 mb-4">⚠️ 시뮬레이션 실패</h1>
            <p className="text-lg text-gray-700">{state.error.message}</p>
            <p className="mt-3 text-sm text-gray-500">디버깅 정보: {JSON.stringify(state.error.details)}</p>
        </div>;
    }

    if (!state.data) {
         return <div className="text-center py-20"><h1 className="text-3xl font-bold">데이터가 없습니다.</h1><p>시뮬레이션을 실행하여 결과를 확인해 주세요.</p></div>;
    }


    return (
        <div className="max-w-4xl mx-auto p-8 bg-gray-50 min-h-screen">
            <header className="text-center mb-10">
                <h1 className="text-4xl font-extrabold text-indigo-800">🛡️ Mini ROI 시뮬레이션</h1>
                <p className="text-lg text-gray-600 mt-2">규제 위협 기반의 재무적 리스크를 즉각적으로 진단합니다.</p>
            </header>

            {/* 1. 입력 폼 섹션 */}
            <Card className="mb-8">
                <h2 className="text-2xl font-bold text-gray-700 mb-4 border-b pb-2">📊 시뮬레이션 변수 설정</h2>
                <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
                    <div>
                        <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">산업 분야</label>
                        <input type="text" name="industry" id="industry" value={params.industry} onChange={handleInputChange} required 
                               className="w-full border p-3 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                    <div>
                        <label htmlFor="marketSizeMillionsUSD" className="block text-sm font-medium text-gray-700 mb-1">시장 규모 (백만 USD)</label>
                        <input type="number" name="marketSizeMillionsUSD" id="marketSizeMillionsUSD" value={params.marketSizeMillionsUSD} onChange={handleInputChange} required 
                               className="w-full border p-3 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                    <div>
                        <label htmlFor="regulatoryComplianceScore" className="block text-sm font-medium text-gray-700 mb-1">규제 준수 점수 (0~100)</label>
                        <input type="number" name="regulatoryComplianceScore" id="regulatoryComplianceScore" value={params.regulatoryComplianceScore} onChange={handleInputChange} required 
                               className="w-full border p-3 rounded focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                </form>
                <Button onClick={handleSubmit} disabled={state.isLoading}>
                    시뮬레이션 실행 및 위험 진단 시작 →
                </Button>
            </Card>

            {/* 2. 결과 출력 섹션 */}
            {state.data && (
                <ResultDisplay result={state.data} />
            )}
        </div>
    );
};

export default SimulationPage;