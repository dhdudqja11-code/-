// Mocking global fetch function for isolated testing
import { renderHook, act } from '@testing-library/react-hooks';
import { useSimulationData } from '../useSimulationData';

// --- MOCK SETUP ---
const mockSuccessResponse = (data: any) => 
    Promise.resolve({ 
        ok: true, 
        status: 200, 
        json: () => Promise.resolve(data) 
    });

const mockFailureResponse = (status: number, message: string) => 
    Promise.resolve({ 
        ok: false, 
        status: status, 
        json: () => Promise.resolve({ message: message }) 
    });


describe('useSimulationData Hook Integration', () => {

    // 테스트 시작 전 fetch를 mock합니다.
    beforeEach(() => {
        jest.spyOn(global, 'fetch').mockImplementation(() => {});
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });


    it('Should successfully run simulation and update data state on success', async () => {
        const mockData = {
            riskGrade: 'Critical', 
            estimatedLossAmountUSD: 150000, 
            mitigationActionPlan: ['규제 감사 실시', '법적 문서 보강']
        };

        // fetch가 성공하는 것처럼 모킹합니다.
        (global.fetch as jest.Mock).mockImplementation(() => mockSuccessResponse(mockData));

        const { result } = renderHook(() => useSimulationData());
        
        // 훅 내부의 runSimulation 함수를 직접 호출하여 테스트 (직접 접근이 필요함)
        await act(async () => {
            result.current.runSimulation({ industry: 'Test', marketSizeMillionsUSD: 10, regulatoryComplianceScore: 50 });
        });

        // 상태가 성공적으로 업데이트되었는지 검증
        expect(result.current.state.isLoading).toBe(false);
        expect(result.current.state.data).toEqual({
            riskGrade: 'Critical',
            estimatedLossAmountUSD: 150000,
            mitigationActionPlan: ['규제 감사 실시', '법적 문서 보강']
        });
    });

    it('Should handle network/API failure (4xx/5xx status code)', async () => {
        // fetch가 실패하는 것처럼 모킹합니다.
        (global.fetch as jest.Mock).mockImplementation(() => mockFailureResponse(403, '권한 부족'));

        const { result } = renderHook(() => useSimulationData());
        
        await act(async () => {
            result.current.runSimulation({ industry: 'Test', marketSizeMillionsUSD: 10, regulatoryComplianceScore: 50 });
        });

        // 상태가 에러로 업데이트되었는지 검증
        expect(result.current.state.isLoading).toBe(false);
        expect(result.current.state.error).toBeDefined();
        expect(result.current.state.error?.message).toContain('API 호출 실패');
    });

    it('Should handle schema mismatch error (missing critical fields)', async () => {
        // 백엔드가 필수 필드를 누락하여 에러를 반환하는 시나리오 모킹
        const mockBadData = { riskGrade: null, estimatedLossAmountUSD: 100 }; // riskGrade가 null인 경우

        (global.fetch as jest.Mock).mockImplementation(() => Promise.resolve({ 
            ok: true, status: 200, json: () => Promise.resolve(mockBadData) 
        }));

        const { result } = renderHook(() => useSimulationData());
        
        await act(async () => {
            result.current.runSimulation({ industry: 'Test', marketSizeMillionsUSD: 10, regulatoryComplianceScore: 50 });
        });

        // 데이터 유효성 검증 로직이 작동하여 에러를 발생시키고 상태가 업데이트되는지 확인
        expect(result.current.state.isLoading).toBe(false);
        expect(result.current.state.error).toBeDefined();
        expect(result.current.state.error?.message).toContain('스키마 불일치');
    });

    it('Should handle network connectivity loss (full fetch rejection)', async () => {
        // 네트워크 연결 자체가 끊어진 시나리오 모킹
        (global.fetch as jest.Mock).mockRejectedValue(new Error("Network request failed"));

        const { result } = renderHook(() => useSimulationData());
        
        await act(async () => {
            result.current.runSimulation({ industry: 'Test', marketSizeMillionsUSD: 10, regulatoryComplianceScore: 50 });
        });

        // 에러 핸들링이 작동했는지 검증
        expect(result.current.state.isLoading).toBe(false);
        expect(result.current.state.error).toBeDefined();
        expect(result.current.state.error?.message).toContain('Network request failed');
    });

});