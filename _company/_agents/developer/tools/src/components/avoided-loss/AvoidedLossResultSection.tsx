// AvoidedLossResultSection.tsx (Client Component)
"use client";

import React, { useState } from 'react';
import LossVisualizationComponent from './LossVisualizationComponent'; // 1. 손실액 시각화 컴포넌트 (Mockup 사용 가정)
import ComplianceAlertComponent from './ComplianceAlertComponent'; // 2. 경고 메시지 컴포넌트 (Mockup 재설계 반영)
import { AvoidedLossSchema } from '@/types/schema'; // API 스키마 정의가 있다고 가정

// Mock API 호출 함수: 실제 백엔드 엔드포인트와 통신할 역할을 합니다.
const fetchAvoidedLossData = async (data: any): Promise<{ success: boolean; data?: any; errors?: any }> => {
    console.log("Simulating API call with input:", data);

    // --- E2E 스트레스 테스트 시나리오 분기 처리 ---

    // 1. 유효성 검증 실패 시나리오 (가장 중요)
    if (!data || !data.inputField || data.inputField === "fail_validation") {
        return {
            success: false,
            errors: [
                {
                    field: "source_data",
                    error_code: "ERR-4001",
                    message: "필수 데이터 누락 또는 형식 오류입니다. (데이터 주권 위반 가능성)",
                    details: "Source ID가 유효하지 않거나, 법적 근거를 증명할 수 있는 메타데이터가 없습니다.",
                    severity: "Critical" // Critical 경고로 강제 표시
                }
            ]
        };
    }

    // 2. API 로직 상의 규제 위반 리스크 발생 시나리오 (Success=false, Alert=true)
    if (data.inputField === "high_risk") {
        return {
            success: false, // 데이터 처리는 성공했으나, 비즈니스/규제상 위험을 발견함
            errors: [
                {
                    field: "regulatory_compliance",
                    error_code: "WARN-2003",
                    message: "데이터 주권 위반 리스크 경고! (Avoided Loss 발생)",
                    details: "사용된 데이터 출처가 특정 지역의 규제(예: GDPR)를 충족하지 못할 수 있습니다. 즉시 검토 필요.",
                    severity: "High" // High 경고로 강제 표시
                }
            ],
            // 성공적으로 계산된 손실액 데이터를 함께 반환하여 통합 시각화에 사용하게 함
            data: { 
                estimated_loss_usd: 15000, 
                risk_factors: [{ name: "GDPR Non-Compliance", value: 9000 }, { name: "Lack of Source Tracking", value: 6000 }]
            }
        };
    }

    // 3. 성공 시나리오 (Success=true, Alert=null)
    return {
        success: true,
        data: { 
            estimated_loss_usd: 4500, // 임시 값
            risk_factors: [{ name: "Poor Data Structure", value: 2000 }, { name: "Missing Consent Log", value: 2500 }]
        }
    };
};


const AvoidedLossResultSection: React.FC = () => {
    const [formData, setFormData] = useState({ inputField: '', description: '' });
    const [result, setResult] = useState<{ success: boolean; data?: any; errors?: any } | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    // 핵심 API 호출 및 상태 업데이트 로직
    const handleCalculateLoss = async (e: React.FormEvent) => {
        e.preventDefault();
        setResult(null); // 초기화

        try {
            // 실제 환경에서는 fetch('/api/v1/avoided_loss', { method: 'POST', body: JSON.stringify(formData) })를 사용합니다.
            const apiResponse = await fetchAvoidedLossData(formData); 
            setResult(apiResponse);

        } catch (error) {
            console.error("API 호출 중 치명적인 에러 발생:", error);
            // 통신 오류 시나리오 처리
            setResult({ success: false, errors: [{ field: "network", error_code: "ERR-5000", message: "서버 연결에 실패했습니다." }] });
        }
    };

    // 렌더링 로직 분기 (핵심)
    const renderContent = () => {
        if (!result) {
            return <div className="p-8 text-center text-gray-500">데이터를 입력하고 '손실액 계산' 버튼을 눌러 결과를 확인하세요.</div>;
        }

        // 1. 규제 경고(Alert)가 존재하는 경우 (최우선 표시)
        if (result.errors && result.errors.length > 0) {
            return (
                <div className="space-y-8">
                    {/* Alert 컴포넌트를 최상단에 강제로 노출 */}
                    <ComplianceAlertComponent alerts={result.errors} /> 
                    
                    {/* 경고가 있더라도, 계산된 데이터(Mitigation Suggestion을 위한 원인)는 보여줘야 함 */}
                    {result.data && (
                        <div>
                            <h3 className="text-xl font-semibold text-red-700 mt-8">📊 발견된 위험 요인 분석</h3>
                            <p>위험 경고에 기반하여 다음의 손실액 시각화 및 원인을 참고해 주십시오.</p>
                            {/* 실제 데이터가 있으므로, LossViz도 렌더링 */}
                            <LossVisualizationComponent data={result.data} isAlertMode={true} />
                        </div>
                    )}

                </div>
            );
        } 
        // 2. 성공적으로 계산되었으나 경고/오류가 없는 경우 (Best Case)
        else if (result.success && result.data) {
            return (
                 <div className="space-y-8">
                    {/* 규제 리스크 컴포넌트는 비활성화 */}
                    <ComplianceAlertComponent alerts={[]} isVisible={false} /> 

                    <div>
                        <h3 className="text-xl font-semibold text-green-700 mt-8">✅ 분석 완료: 예상 손실액 시각화</h3>
                        <p>현재 데이터 구조 및 프로세스를 유지할 경우, 추정되는 잠재적 법률/규제 리스크에 의한 손실은 다음과 같습니다.</p>
                         {/* 성공적으로 계산된 데이터를 LossViz에 전달 */}
                        <LossVisualizationComponent data={result.data} isAlertMode={false} /> 
                    </div>
                </div>
            );
        }

        // 3. 기타 에러 처리 (네트워크 등)
        return <div className="text-red-600">결과를 처리하는 중 오류가 발생했습니다. 콘솔 로그를 확인해 주세요.</div>;
    };


    return (
        <section id="avoided-loss-calculator" className="py-16 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 className="text-3xl font-extrabold text-gray-900 mb-4">💰 내가 모르는 사이 발생하는 손실 (Avoided Loss) 진단</h2>
                <p className="text-lg text-gray-500 mb-10">귀사의 현재 데이터 처리 구조가 법적/규제 리스크에 노출되는 정도를 실시간으로 진단합니다.</p>

                {/* 입력 폼 */}
                <div className="bg-white p-8 rounded-xl shadow-2xl border border-gray-100 mb-12">
                    <h3 className="text-2xl font-bold text-indigo-700 mb-6">🔍 데이터 진단 입력</h3>
                    <form onSubmit={handleCalculateLoss} className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
                        {/* 시뮬레이션용 필드 1: 유효성 검증 실패 테스트 */}
                        <div>
                            <label htmlFor="inputField" className="block text-sm font-medium text-gray-700 mb-2">테스트 모드 (필수)</label>
                            <select id="inputField" name="inputField" onChange={handleChange} value={formData.inputField} required 
                                className="mt-1 block w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
                                <option value="">[테스트 선택]</option>
                                <option value="" disabled>실제 데이터 입력</option>
                                <option value="fail_validation">🚨 유효성 검증 실패 (ERR-4001)</option>
                                <option value="high_risk">⚠️ 규제 위반 리스크 발생 (WARN-2003)</option>
                            </select>
                        </div>

                        {/* 시뮬레이션용 필드 2: 일반 설명 */}
                        <div>
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">데이터 출처/설명 (예시)</label>
                            <input type="text" id="description" name="description" value={formData.description} onChange={handleChange} required 
                                className="mt-1 block w-full p-3 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500" placeholder="예: 미국 개인정보 보호법에 따른 고객 동의 로그">
                        </div>

                        {/* 버튼 */}
                        <button 
                            type="submit" 
                            className={`w-full py-3 px-6 border border-transparent rounded-md shadow-sm text-base font-medium transition duration-150 ${result ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-indigo-500 hover:bg-indigo-600'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                        >
                            손실액 계산 및 리스크 진단 실행 ⚙️
                        </button>
                    </form>
                </div>

                {/* 결과 섹션 (동적 렌더링) */}
                <div className="mt-12">
                    {renderContent()}
                </div>
            </div>
        </section>
    );
};

export default AvoidedLossResultSection;