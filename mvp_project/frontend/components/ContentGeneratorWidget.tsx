// Next.js / React Component Skeleton
import React, { useState } from 'react';

interface ContentInputProps {}

const ContentGeneratorWidget: React.FC = () => {
    const [step, setStep] = useState(1); // 1: 입력 -> 2: 옵션 설정 -> 3: 결과 보기
    const [isLoading, setIsLoading] = useState(false);

    // Step 1: 핵심 키워드 및 콘텐츠 유형 정의 (필수)
    const renderStepOne = () => (
        <section className="p-6 border rounded shadow-sm">
            <h2 className="text-xl font-bold mb-4">🎯 1단계: 주제 설정</h2>
            {/* Keyword Input */}
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700">핵심 키워드 (필수)</label>
            <input type="text" id="keyword" placeholder="예: AI 프롬프트 엔지니어링의 미래 구조" className="mt-1 block w-full border p-2 rounded"/>

            {/* Content Type Selector */}
            <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">콘텐츠 형식 선택</label>
                <select className="w-full border p-2 rounded">
                    <option value="blog">📖 전문 블로그 포스팅 (Long Form)</option>
                    <option value="sns">🔗 SNS 홍보용 카드 뉴스 초안 (Short Form)</option>
                    <option value="report">📈 사업 보고서/기획서 구조화</option>
                </select>
            </div>
        </section>
    );

    // Step 2: 세부 옵션 및 페르소나 정의 (선택적)
    const renderStepTwo = () => (
        <section className="p-6 border rounded shadow-sm">
             <h2 className="text-xl font-bold mb-4">⚙️ 2단계: 세부 아키텍처 설정</h2>
            {/* Persona Input */}
            <div className="mb-4 p-3 bg-gray-50 rounded">
                <label className="block text-sm font-medium text-gray-700 mb-1">타겟 페르소나 (누구에게 보여줄 글인가요?)</label>
                {/* Dropdowns or Textarea for Age/Job */}
            </div>

             {/* Tone Input */}
            <div className="mb-4 p-3 bg-gray-50 rounded">
                <label className="block text-sm font-medium text-gray-700 mb-1">톤앤매너</label>
                <select className="w-full border p-2 rounded">
                    <option>전문적/권위적 (Academic)</option>
                    <option selected>친근하고 공감 위주 (Empathetic)</option>
                    {/* ... other options */}
                </select>
            </div>

            {/* Submit Button to API */}
            <button onClick={() => { 
                setIsLoading(true); 
                // Mock API Call: POST /api/v1/generate_content
                setTimeout(() => { 
                    setIsLoading(false); 
                    setStep(3); 
                }, 2000);
            }} className="w-full p-3 bg-indigo-600 text-white rounded hover:bg-indigo-700">
                ✅ 구조화된 초안 생성 시작 (API 호출)
            </button>
        </section>
    );

    // Step 3: 결과 출력 및 검토 (Result Viewer)
    const renderStepThree = () => (
        <section className="p-6 border rounded shadow-sm bg-green-50">
             <h2 className="text-xl font-bold mb-4 text-green-800">✅ 3단계: 완성된 구조 초안 확인</h2>
            {/* Placeholder for Markdown/HTML Output */}
            <div className="prose max-w-none bg-white p-6 rounded border mt-4">
                <h3>[✨ 생성된 제목]</h3>
                <p>AI 프롬프트 엔지니어링: 2025년 시장에서 살아남는 '아키텍처' 설계법</p>
                {/* Structure Preview */}
                <h4>I. 문제 제기: 왜 기존의 글쓰기는 실패하는가?</h4>
                <p>[... 본문 초안 내용 ...]</p>
                 {/* CTA Buttons */}
                <button className="mr-2 p-2 bg-yellow-500 text-white">다운로드 (MD/DOCX)</button>
                <button className="p-2 border rounded" onClick={() => setStep(1)}>다시 수정</button>
            </div>
        </section>
    );

    return (
        <div className="max-w-3xl mx-auto">
            {step === 1 && renderStepOne()}
            {step === 2 && renderStepTwo()}
            {step === 3 && renderStepThree()}
        </div>
    );
};

export default ContentGeneratorWidget;