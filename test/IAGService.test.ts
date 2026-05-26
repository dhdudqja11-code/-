// test/IAGService.test.ts

import { ImmutableAuditGateway } from '../src/services/ImmutableAuditGateway';

/**
 * IAG Service 통합 테스트 스위트.
 * 목표: 성공, 체인 무결성 실패, 데이터 유효성 실패 케이스를 모두 커버하여 법적 증명력을 확보한다.
 */
describe('🛡️ Immutable Audit Gateway (IAG) v1.0 E2E Test', () => {

    // 초기 블록의 해시 값은 이 시스템의 기준이 된다.
    const INITIAL_HASH = "0000_INITIAL_AUDIT_BLOCK"; 
    
    /**
     * 성공 케이스: 모든 검증 통과 시 AuditBlock 생성 및 반환 테스트
     */
    test('✅ [SUCCESS] 유효한 트랜잭션 페이로드를 제출했을 때, AuditBlock이 정상적으로 생성되어야 한다.', () => {
        const payload = {
            transactionId: "TX-20260526-A",
            timestamp: Date.now(),
            data: { user: "admin", action: "privilege_upgrade" },
            previousBlockHash: INITIAL_HASH, // 유효한 이전 블록 해시 사용
        };

        const result = ImmutableAuditGateway.submitAuditRequest(payload);

        expect(result.success).toBe(true);
        expect(result.block).not.toBeNull();
        // 생성된 블록의 내용은 트랜잭션 데이터와 일치하는지 확인 (데이터 무결성)
        expect(JSON.stringify(result.block.data)).toContain("privilege_upgrade"); 
    });

    /**
     * 실패 케이스 1: 체인 해싱 무결성 검증 실패 테스트
     * 이전 블록의 해시가 현재 게이트웨이가 예상하는 값과 다를 경우 (체이닝 단절)
     */
    test('❌ [FAIL] 유효하지 않은 previousBlockHash를 제출했을 때, 트랜잭션은 거부되어야 한다.', () => {
        const payload = {
            transactionId: "TX-FAILURE-CHAIN",
            timestamp: Date.now(),
            data: { user: "test", action: "attempted_bypass" },
            previousBlockHash: "INVALID_OR_MANIPULATED_HASH_12345", // 의도적으로 잘못된 해시 사용
        };

        const result = ImmutableAuditGateway.submitAuditRequest(payload);

        expect(result.success).toBe(false);
        // 예상하는 에러 메시지 구조 확인 (Problem Definition)
        expect(result.message).toContain("400 BAD REQUEST: Invalid previousBlockHash"); 
    });


    /**
     * 실패 케이스 2: 데이터 유효성 검증 실패 테스트
     * 트랜잭션 데이터 자체가 필수 필드를 갖추지 않았을 경우 (데이터 무결성)
     */
    test('⚠️ [FAIL] 필수 데이터를 누락한 페이로드를 제출했을 때, 전처리 단계에서 거부되어야 한다.', () => {
        const payload = {
            transactionId: "TX-FAILURE-DATA",
            timestamp: Date.now(),
            data: null, // 데이터 필드 누락/무효화
            previousBlockHash: INITIAL_HASH, 
        };

        const result = ImmutableAuditGateway.submitAuditRequest(payload);

        expect(result.success).toBe(false);
        // 예상하는 에러 메시지 구조 확인 (Problem Definition)
        expect(result.message).toContain("422 UNPROCESSABLE ENTITY: Transaction data failed internal validation rules."); 
    });
    
     /**
     * 실패 케이스 3: 인증/권한 검증 실패 테스트 (JWT Mocking)
     */
    test('🛑 [FAIL] 유효하지 않은 권한(Mock JWT failure)을 가진 요청은 거부되어야 한다.', () => {
        const payload = {
            transactionId: "INVALID-AUTH", // 모의 인증 실패 ID 사용
            timestamp: Date.now(),
            data: { user: "attacker", action: "steal_data" },
            previousBlockHash: INITIAL_HASH, 
        };

        const result = ImmutableAuditGateway.submitAuditRequest(payload);

        expect(result.success).toBe(false);
        // 예상하는 에러 메시지 구조 확인 (Problem Definition)
        expect(result.message).toContain("401 UNAUTHORIZED: Missing or invalid JWT signature/expiry."); 
    });
});