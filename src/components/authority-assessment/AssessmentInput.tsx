import React from 'react';

interface AssessmentInputProps {
    formData: {
        regulatoryRisk: number;
        dataIntegrityCheck: boolean;
        systemAuditScore: number;
    };
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const AssessmentInput: React.FC<AssessmentInputProps> = ({ formData, onChange }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Input 1: 규제 위험 레벨 (Range Slider) */}
            <div>
                <label htmlFor="regulatoryRisk" className="block text-sm font-medium text-gray-700 mb-2">
                    규제 리스크 점수 측정 (Regulatory Risk Level, 1~5):
                </label>
                <input
                    type="range"
                    id="regulatoryRisk"
                    name="regulatoryRisk"
                    min="1"
                    max="5"
                    step="1"
                    value={formData.regulatoryRisk}
                    onChange={(e) => onChange(e)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer focus:ring-red-500 focus:border-red-500"
                />
                <div className="flex justify-between text-xs mt-1 text-gray-500"><span>최소 (Low Risk)</span> <span>최대 (High Risk)</span></div>
            </div>

            {/* Input 2: 데이터 무결성 검사 여부 (Checkbox - 중요 트래킹 포인트) */}
            <div className="flex items-start p-3 bg-red-50 rounded border border-red-200">
                <input
                    id="dataIntegrityCheck"
                    name="dataIntegrityCheck"
                    type="checkbox"
                    checked={formData.dataIntegrityCheck}
                    onChange={(e) => onChange(e)}
                    className="h-5 w-5 text-red-600 border-gray-300 mt-1 flex-shrink-0"
                />
                <div className="ml-3 text-sm">
                    <label htmlFor="dataIntegrityCheck" className="font-medium text-gray-700">데이터 무결성 검사 완료</label>
                    <p className='text-xs text-red-500'>✅ (권위 증명 핵심 요소) 원본 데이터의 변조 여부를 확인했습니까?</p>
                </div>
            </div>

            {/* Input 3: 시스템 감사 점수 (Slider/Number Input) */}
            <div>
                <label htmlFor="systemAuditScore" className="block text-sm font-medium text-gray-700 mb-2">
                    시스템 내부 통제 감사 점수 (System Audit Score, 0~100):
                </label>
                 <input
                    type="range"
                    id="systemAuditScore"
                    name="systemAuditScore"
                    min="0"
                    max="100"
                    step="1"
                    value={formData.systemAuditScore}
                    onChange={(e) => onChange(e)}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer focus:ring-green-500 focus:border-green-500"
                />
                <div className="flex justify-between text-xs mt-1 text-gray-500"><span>최저 (Low)</span> <span>최고 (Perfect)</span></div>
            </div>
        </div>
    );
};

export default AssessmentInput;