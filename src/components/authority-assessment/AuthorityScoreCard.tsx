import React from 'react';

interface ScoreCardProps {
    score: number;
    state: string; // IDLE, WARNING, AUTHORITY
}

const getStatusClasses = (state: string) => {
    switch(state) {
        case 'WARNING': return "text-red-600 border-red-300 bg-red-50";
        case 'AUTHORITY': return "text-green-700 border-green-300 bg-green-50";
        case 'IDLE': default: return "text-blue-600 border-blue-300 bg-blue-50";
    }
};

const getStatusLabel = (state: string) => {
    switch(state) {
        case 'WARNING': return "🚨 경고 (Warning)";
        case 'AUTHORITY': return "✅ 통제권 확보 (Authority)";
        case 'IDLE': default: return "⚫ 미진단 (Idle)";
    }
};


const AuthorityScoreCard: React.FC<ScoreCardProps> = ({ score, state }) => {
    const statusClasses = getStatusClasses(state);

    return (
        <div className={`p-6 rounded-xl shadow-lg border-4 ${statusClasses}`}>
            <div className="flex justify-between items-center mb-2">
                <h3 className="text-2xl font-extrabold uppercase tracking-wider">{getStatusLabel(state)}</h3>
                {/* 시각적 권위 증명 요소를 위한 네온 글리치 효과 Placeholder */}
                <span className="text-sm bg-opacity-80 px-3 py-1 rounded-full border border-dashed animate-pulse">
                    [Authority Meter] ⚡️
                </span>
            </div>
            
            <div className="flex items-end justify-between pt-4 border-t border-dashed">
                <span className="text-lg font-medium text-gray-600">최종 Authority Score:</span>
                <span className={`text-5xl font-black ${state === 'AUTHORITY' ? 'text-green-800' : state === 'WARNING' ? 'text-red-700' : 'text-blue-600'}`}>
                    {score} / 100
                </span>
            </div>

             <p className="mt-4 text-sm italic border-t pt-2 text-gray-500">
                 * 이 점수는 시스템적 리스크 데이터를 바탕으로 구조화된 진단 결과를 나타냅니다.
             </p>
        </div>
    );
};

export default AuthorityScoreCard;