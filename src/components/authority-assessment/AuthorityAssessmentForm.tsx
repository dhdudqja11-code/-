import React, { useState } from 'react';
import AuthorityScoreCard from './AuthorityScoreCard';
import AssessmentInput from './AssessmentInput';
// Mocking API calls and tracking functions for the mockup stage

/**
 * @typedef {'IDLE' | 'WARNING' | 'AUTHORITY'} AuthorityState
 */

// --- MOCK UTILITIES ---
// 실제로는 Context나 Redux에서 가져오거나, 서버 함수 호출로 대체됨.
const trackEvent = (eventName, properties) => {
    console.log(`[TRACKING] Event: ${eventName}`, properties);
};

/** 
 * 가상의 API 호출 시뮬레이션. 백엔드 로직을 모방함.
 * @param {Object} formData - 사용자가 입력한 데이터
 * @returns {{score: number, state: AuthorityState, message: string}} 상태와 스코어를 반환하는 객체
 */
const calculateAuthorityScore = (formData) => {
    // 🚨 이 로직은 실제 backend API Gateway 호출(POST /api/v1/calculate_authority)을 대체합니다.
    let score = 0;
    if (formData.regulatoryRisk > 3 && formData.dataIntegrityCheck === true) {
        score = Math.floor((formData.regulatoryRisk + 2) * 10); // WARNING 레벨 시뮬레이션
    } else if (formData.systemAuditScore >= 90) {
        score = 100; // AUTHORITY 레벨 시뮬레이션
    } else {
        score = Math.floor(Math.random() * 50); // IDLE 또는 미진단 상태 시뮬레이션
    }

    let state = 'IDLE';
    let message = "평가 대기 중입니다.";

    if (score < 40) {
        state = 'IDLE';
        message = "시스템 기초 점검이 필요합니다. 기본 데이터를 입력해주세요.";
    } else if (score >= 40 && score < 90) {
        // WARNING state logic: 불안감 고조 및 문제 정의/원인 분석 강조
        state = 'WARNING';
        message = `🚨 경고! 현재 시스템의 통제권 점수는 ${score}점입니다. 구조적 취약성이 감지되었습니다. 원인을 진단하고 권위를 확보해야 합니다.`;
    } else {
        // AUTHORITY state logic: 성공과 통제력 재확립 강조
        state = 'AUTHORITY';
        message = `✅ 축하합니다! 시스템의 모든 핵심 지표가 검증되었으며, 현재 ${score}점의 높은 권위 수준을 확보했습니다.`;
    }

    trackEvent('authority_score_calculated', { score: score, state: state });
    return { score, state, message };
};


const AuthorityAssessmentForm = () => {
    // 초기 상태는 IDLE로 설정합니다.
    const [formData, setFormData] = useState({
        regulatoryRisk: 1, // 1-5 (가정)
        dataIntegrityCheck: false, // boolean
        systemAuditScore: 0 // 0-100
    });
    const [assessmentResult, setAssessmentResult] = useState(null);

    // 입력 필드 변경 핸들러
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : (name === 'regulatoryRisk' ? parseInt(value) : parseFloat(value))
        }));
    };

    // 평가 실행 로직
    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("--- ⚙️ Authority Assessment 시작 ---");

        // 1. 입력 유효성 검사 및 데이터 전송 시뮬레이션
        trackEvent('assessment_submitted', formData);
        
        // 2. 백엔드 API 호출 시뮬레이션 (비동기)
        const result = calculateAuthorityScore(formData);
        
        setAssessmentResult({
            score: result.score,
            state: result.state,
            message: result.message
        });

        console.log("--- 🔬 평가 완료 ---");
    };


    // 상태에 따른 UI 분기 처리 (핵심 UX Flow)
    const renderContent = () => {
        if (!assessmentResult) {
            return <p className="text-gray-500 p-4 bg-yellow-50/50">데이터를 입력하고 '평가 시작' 버튼을 눌러 시스템 진단을 요청해주세요.</p>;
        }

        // 🟢 AUTHORITY State (권위 확보 과정)
        if (assessmentResult.state === 'AUTHORITY') {
            return <div className="text-green-700 bg-green-50/60 p-6 border-l-4 border-green-600">
                <h3 className="font-bold text-xl mb-2">🎉 통제권 확보 완료: [최고 권위 상태]</h3>
                <p>{assessmentResult.message}</p>
                <p className="mt-3 font-semibold">[마이크로 카피]: 당신의 시스템은 외부 위협으로부터 완벽히 보호되고 있습니다.</p>
            </div>;
        } 
        // 🟡 WARNING State (불안감 고조 및 진단)
        else if (assessmentResult.state === 'WARNING') {
            return <div className="text-red-700 bg-red-50/60 p-6 border-l-4 border-yellow-600">
                <h3 className="font-bold text-xl mb-2 flex items-center"><span className="mr-2 animate-pulse">🚨</span> 시스템 경고: [위험 감지]</h3>
                <p>{assessmentResult.message}</p>
                 <p className="mt-3 font-semibold">[마이크로 카피]: 지금 바로 취약점을 진단하고 통제권을 재확립해야 합니다. 이대로 방치하면 운영 중단 위험에 직면할 수 있습니다.</p>
            </div>;
        } 
        // ⚫ IDLE State (기초 단계)
        else {
             return <div className="text-blue-700 bg-blue-50/60 p-6 border-l-4 border-blue-600">
                <h3 className="font-bold text-xl mb-2">🔍 진단 준비 단계</h3>
                <p>{assessmentResult.message}</p>
                <p class="mt-3 font-semibold">[마이크로 카피]: 핵심 데이터를 충분히 입력해야 정확한 시스템 위험도를 측정할 수 있습니다.</p>
            </div>;
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8 bg-white shadow-2xl rounded-lg">
            <h1 className="text-3xl font-bold text-gray-900 mb-6 border-b pb-2">🛡️ Authority Score Pre-Assessment</h1>
            <p className="mb-8 text-sm text-gray-600">[목표]: 시스템의 구조적 취약성을 진단하고, '통제권 확보 과정(Authority)'에 대한 필요성을 인지시키는 것이 목적입니다.</p>

            {/* 1. 입력 섹션 */}
            <section className="mb-10 p-6 border rounded-lg bg-gray-50">
                <h2 className="text-xl font-semibold mb-4 text-indigo-700">📊 시스템 진단 데이터 입력 (사용자 액션 유도)</h2>
                <form onSubmit={handleSubmit}>
                    {/* Input Component가 역할 분담을 할 것이므로, 여기는 구조만 정의합니다. */}
                    <AssessmentInput 
                        formData={formData} 
                        onChange={handleInputChange} 
                    />

                    <button 
                        type="submit" 
                        className={`mt-8 w-full py-3 rounded-lg text-white font-bold transition duration-200 ${assessmentResult ? 'bg-gray-400 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700'}`}
                        disabled={!assessmentResult}
                    >
                        {assessmentResult ? "진단 결과 확인 완료" : "시스템 진단 시작 (권위 측정)"}
                    </button>
                </form>
            </section>

            {/* 2. 결과 및 피드백 섹션 */}
            <section className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-indigo-700 border-b pb-2">💡 진단 결과 & 사용자 여정 (UX Flow)</h2>
                {renderContent()}
            </section>

             {/* 3. 트래킹 포인트 강조 */}
             <div className="mt-10 p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                 <h3 class="font-bold text-lg text-gray-800 mb-2">⚠️ 개발자 참고: 트래킹 Hook Points</h3>
                 <p className='text-sm'>위의 `trackEvent` 함수가 호출되는 지점들은 반드시 A/B 테스트를 위한 추적 이벤트(e.g., `assessment_submitted`, `authority_score_calculated`)로 활용되어야 합니다.</p>
             </div>

        </div>
    );
};

export default AuthorityAssessmentForm;