import { validateAndLogTransaction } from '../services/TransactionValidator';

// --- Test Case 1: 인증 실패 (가장 단순한 Failure) ---
async function testAuthFailure() {
    console.log("=============================");
    console.log("=== 테스트 케이스 1: JWT 만료/위조 시도 ===");
    const result = await validateAndLogTransaction("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "USER_A_DATA");
    if (!result.success && result.auditRecord) {
        console.log("\n[✅ PASS] 인증 실패 감지 및 감사 기록 생성 성공.");
        console.log("--- Audit Block Preview ---");
        console.log(JSON.stringify(result.auditRecord, null, 2));
    } else {
        console.error("[❌ FAIL] 인증 실패 트랜잭션에서 감사 기록을 받지 못했습니다.");
    }
}

// --- Test Case 2: 권한 부재 (리소스 소유권 위반) ---
async function testAuthorizationFailure() {
    console.log("\n=============================");
    console.log("=== 테스트 케이스 2: User A가 User B 자원 접근 시도 ===");
    // AuthManager는 유효하지만, Resource ID 자체가 문제를 일으키게 Mocking함.
    const result = await validateAndLogTransaction("valid_jwt_token_for_user_a", "USER_B_SECRET_DATA");
     if (!result.success && result.auditRecord) {
        console.log("\n[✅ PASS] 권한 부재(Resource Violation) 감지 및 감사 기록 생성 성공.");
        console.log("--- Audit Block Preview ---");
        console.log(JSON.stringify(result.auditRecord, null, 2));
    } else {
        console.error("[❌ FAIL] 권한 부재 트랜잭션에서 감사 기록을 받지 못했습니다.");
    }
}

// --- Test Case 3: 성공 케이스 (Happy Path) ---
async function testSuccessCase() {
    console.log("\n=============================");
    console.log("=== 테스트 케이스 3: 모든 검증 통과 시도 ===");
    const result = await validateAndLogTransaction("valid_jwt_token_for_user_a", "USER_A_OWN_DATA");
     if (result.success) {
        console.log("\n[✅ PASS] 성공 트랜잭션이 정상적으로 처리되었습니다.");
    } else {
         console.error("[❌ FAIL] 예상치 않게 실패했습니다. 로그 확인 필요.");
    }
}

(async () => {
    await testAuthFailure();
    await testAuthorizationFailure();
    await testSuccessCase();
})();