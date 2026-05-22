import React, { useState } from 'react';
import axios from 'axios'; // API 호출용 라이브러리 (가정)

// 백엔드에서 정의한 구조체를 TypeScript 인터페이스로 재현
interface MiniRoiResult {
    status: "WARNING" | "SAFE";
    risk_score: number;
    problem_definition: string;
    cause_analysis: string;
    mitigation_suggestion: string;
}

const MiniRoiSimulator: React.FC = () => {
    const [formData, setFormData] = useState({
        userIndustry: '',
        dataVolumeGb: 0,
        regulatoryRiskScore: 1, // 초기값 안전하게 설정
    });
    const [result, setResult] = useState<MiniRoiResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // 입력 값 변경 핸들러
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value === '' ? 0 : parseFloat(e.target.value) || parseInt(e.target.value),
        });
    };

    // 시뮬레이션 실행 핸들러
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            // 실제 백엔드 URL로 변경 필요
            const response = await axios.post<MiniRoiResult>(
                'http://localhost:8000/mini-roi/', // <--- API Gateway 주소 확인 필요
                formData
            );
            setResult(response.data);

        } catch (err) {
            console.error("API 호출 실패:", err);
            setError("데이터 전송에 실패했습니다. 백엔드 서비스가 정상 작동하는지 확인해 주세요.");
        } finally {
            setIsLoading(false);
        }
    };

    // --------------------
    // UX 컴포넌트 렌더링 로직
    // --------------------
    const renderResultContent = () => {
        if (!result) return null;

        const isWarning = result.status === "WARNING";
        // 경고/위기 상태는 남색 배경에 오렌지 강조 (회사의 규정 컬러 활용)
        const containerClass = isWarning ? "bg-blue-900/80 border-red-500" : "bg-green-100 border-gray-300";

        return (
            <div className={`p-6 rounded-lg shadow-2xl ${containerClass} mt-8`}>
                <h2 className="text-2xl font-bold mb-4 text-white">{isWarning ? "⚠️ 심각한 규제 리스크 경고 발생!" : "✅ 데이터 관리 안정성 진단 완료"}</h2>

                {/* 1. 종합 위험 점수 시각화 */}
                <div className="mb-6 p-4 bg-white rounded shadow flex justify-between items-center">
                    <span className={`text-xl font-semibold ${isWarning ? 'text-red-700' : 'text-green-700'}`}>
                        종합 리스크 점수: {result.risk_score} / 10
                    </span>
                    {/* 실제 구현에서는 여기에 리스크 막대 그래프가 들어가야 함 */}
                </div>

                <div className="space-y-6">
                    {/* [1] 문제 정의 (Problem) - 공포 조성 */}
                    <section>
                        <h3 className="text-xl font-semibold text-red-800 border-b pb-1 mb-2">🚨 1. 발견된 문제점 (What went wrong?)</h3>
                        <p className="text-gray-700 italic">{result.problem_definition}</p>
                    </section>

                    {/* [2] 원인 분석 (Cause) - 권위성 제시 */}
                    <section>
                        <h3 className="text-xl font-semibold text-blue-800 border-b pb-1 mb-2">🔍 2. 근본 원인 및 출처 분석 (Why did it go wrong?)</h3>
                        <p className="text-gray-600">{result.cause_analysis}</p>
                    </section>

                    {/* [3] 해결책 제시 (Solution) - CTA 유도 */}
                    <section>
                        <h3 className="text-xl font-semibold text-green-800 border-b pb-1 mb-2">💡 3. 필수 개선 액션 플랜 (How to fix it?)</h3>
                        <p className="text-gray-700 bg-yellow-100 p-3 rounded border-l-4 border-yellow-500">{result.mitigation_suggestion}</p>
                    </section>
                </div>

                {/* 최종 CTA 버튼 (가장 중요) */}
                <button className="mt-8 w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded transition duration-200 shadow-lg">
                    🚨 지금, 법적 리스크 무료 진단받기 (Mini ROI)
                </button>
            </div>
        );
    };

    return (
        <div className="max-w-3xl mx-auto p-8 bg-white shadow-xl rounded-xl">
            <h1 className="text-3xl font-extrabold mb-6 text-center border-b pb-2">📊 Mini ROI 리스크 시뮬레이션</h1>
            <p className="mb-8 text-gray-600 text-center">보유 데이터와 현재 규제 환경을 입력하여 잠재적 법적 손실액을 진단하세요.</p>

            {/* 폼 섹션 */}
            <form onSubmit={handleSubmit} className="space-y-6 p-6 border rounded-lg shadow-inner">
                <div>
                    <label htmlFor="userIndustry" className="block text-sm font-medium text-gray-700">산업군 (예: 금융, 의료, 이커머스)</label>
                    <input 
                        type="text" 
                        name="userIndustry" 
                        id="userIndustry" 
                        value={formData.userIndustry} 
                        onChange={handleChange} 
                        required 
                        className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="dataVolumeGb" className="block text-sm font-medium text-gray-700">데이터 볼륨 (GB) <span className='text-red-500'>*필수</span></label>
                        <input 
                            type="number" 
                            name="dataVolumeGb" 
                            id="dataVolumeGb" 
                            value={formData.dataVolumeGb} 
                            onChange={handleChange} 
                            required 
                            min="0"
                            step="0.1"
                            className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                    <div>
                        <label htmlFor="regulatoryRiskScore" className="block text-sm font-medium text-gray-700">자가 진단 리스크 점수 (1~10) <span className='text-red-500'>*필수</span></label>
                        <input 
                            type="number" 
                            name="regulatoryRiskScore" 
                            id="regulatoryRiskScore" 
                            value={formData.regulatoryRiskScore} 
                            onChange={handleChange} 
                            required 
                            min="1"
                            max="10"
                            className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                </div>

                <button 
                    type="submit" 
                    disabled={isLoading}
                    className={`w-full py-3 px-4 rounded-md text-white font-bold transition duration-150 ${
                        isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                >
                    {isLoading ? "🔍 리스크 분석 중... 잠시만 기다려 주세요." : "📊 Mini ROI 시뮬레이션 실행"}
                </button>
            </form>

            {/* 에러 메시지 표시 */}
            {error && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3 mt-6" role="alert">
                    <p className="font-bold">⚠️ 시스템 오류:</p>
                    <p>{error}</p>
                </div>
            )}

            {/* 결과 표시 */}
            {result && renderResultContent()}
        </div>
    );
};

export default MiniRoiSimulator;