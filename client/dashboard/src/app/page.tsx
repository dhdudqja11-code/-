import DashboardLayout from '@/components/DashboardLayout';
// 임시 컴포넌트: 실제 API 호출 로직이 들어갈 곳
const RiskInputForm = () => (
  <div className="bg-white p-8 shadow-lg rounded-xl mb-10 border-t-4 border-blue-600">
    <h2 className="text-2xl font-semibold text-gray-800 mb-4">🛡️ 위험 진단 데이터 입력</h2>
    <p className="mb-6 text-sm text-gray-500">다음 변수를 최대한 정확하게 입력해주세요. (API Gateway 연동 예정)</p>
    {/* 실제 폼 요소는 추후 개발 */}
    <div className="grid grid-cols-3 gap-6">
      <div>
        <label htmlFor="source_risk" className="block text-sm font-medium text-gray-700">1. 원천 리스크 점수 (Source Risk Score)</label>
        <input type="number" id="source_risk" defaultValue={85} className="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/>
      </div>
       <div>
        <label htmlFor="reg_cost" className="block text-sm font-medium text-gray-700">2. 규제 준수 비용 (Regulatory Cost)</label>
        <input type="number" id="reg_cost" defaultValue={1200} className="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/>
      </div>
       <div>
        <label htmlFor="rep_factor" className="block text-sm font-medium text-gray-700">3. 명성 손실 계수 (Reputation Factor)</label>
        <input type="number" id="rep_factor" defaultValue={5} className="mt-1 block w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/>
      </div>
    </div>
    <button className="mt-8 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-150">
      ✅ Avoided Loss 계산 실행
    </button>
  </div>
);

// 메인 페이지 컴포넌트
export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="max-w-full">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-2">📈 재무적 위험 회피 비용 분석 대시보드</h1>
        <p className="text-lg text-blue-600 border-b pb-4 mb-8">Avoided Loss Calculator (MVP)</p>

        {/* 1. 입력 섹션 */}
        <RiskInputForm />

        {/* 2. 결과 출력 영역 (가상의 API 호출 결과를 보여줄 자리) */}
        <div className="bg-white p-8 shadow-lg rounded-xl border-t-4 border-green-600">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center">
             📊 계산 결과: <span className='ml-3 text-green-700'>₩1,520,000 예상 회피 손실액</span>
          </h2>
          <p className="text-lg text-gray-600 mb-4">시스템이 분석한 잠재적 재무적 위험과 이를 방지하기 위한 최적의 솔루션 도입 필요성을 보여줍니다.</p>

          {/* 결과 상세 카드가 들어갈 곳 */}
        </div>
      </div>
    </DashboardLayout>
  );