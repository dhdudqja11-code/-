/**
 * @fileoverview PoC 트랜잭션 검증 서비스 (Mocked Environment).
 * JWT 유효성 및 비즈니스 로직 실패 시, 불변 감사 블록 생성을 시뮬레이션합니다.
 * 실제 DB 연결 없이, 핵심 보안 로직의 통합 테스트를 목표로 합니다.
 */

import { AuthManager } from './AuthManager';
import { AuditLogger } from './AuditLogger';

/**
 * 트랜잭션 검증 및 감사 블록 생성을 시뮬레이션합니다.
 * @param jwtToken - 클라이언트가 제출한 JWT 토큰.
 * @param attemptedResourceId - 사용자가 접근을 시도한 자원 ID (예: User B의 데이터).
 * @returns {Promise<{ success: boolean, auditRecord?: any }>} 검증 결과와 감사 레코드(실패 시)를 포함합니다.
 */
export async function validateAndLogTransaction(jwtToken: string, attemptedResourceId: string): Promise<{ success: boolean, auditRecord?: any }> {

    console.log("--- [PoC] 트랜잭션 검증 시작 ---");
    let validationSuccessful = false;
    let failureReason: string = "";
    let failedAuditLog: any = null;

    try {
        // 1. JWT 유효성 및 권한 체크 (AuthManager 사용)
        const authResult = await AuthManager.verifyToken(jwtToken);

        if (!authResult.isValid || !authResult.isAuthorizedForResource(attemptedResourceId)) {
            failureReason = `[AUTH_FAILURE] 인증 실패 또는 자원 접근 권한 부재. (유효성: ${authResult.isValid ? 'OK' : 'FAIL'}, 승인: ${authResult.isAuthorized ? 'YES' : 'NO'})`;
            console.warn(`⚠️ [PoC Failure Simulation]: ${failureReason}`);

            // 2. 실패 시 감사 로깅 트리거 (AuditLogger 사용)
            failedAuditLog = await AuditLogger.createFailureAuditBlock(
                "Authentication/Authorization Attempt Failed",
                {
                    source_ip: "192.168.0.1", // Mocked IP
                    attempted_user: authResult.userId || 'UNKNOWN',
                    resource_id: attemptedResourceId,
                    error_detail: failureReason,
                    timestamp: new Date().toISOString()
                }
            );

            return { success: false, auditRecord: failedAuditLog };
        }

        // 3. 비즈니스 로직 검증 (Mocking)
        if (attemptedResourceId.startsWith('USER_B')) {
             failureReason = `[BUSINESS_FAILURE] 사용자가 소유하지 않은 자원 ID (${attemptedResourceId}) 접근 시도 감지.`;
             console.warn(`⚠️ [PoC Failure Simulation]: ${failureReason}`);

            // 2. 실패 시 감사 로깅 트리거 (AuditLogger 사용)
            failedAuditLog = await AuditLogger.createFailureAuditBlock(
                "Business Logic Violation",
                {
                    source_ip: "192.168.0.1", // Mocked IP
                    attempted_user: authResult.userId,
                    resource_id: attemptedResourceId,
                    error_detail: failureReason,
                    timestamp: new Date().toISOString()
                }
            );

            return { success: false, auditRecord: failedAuditLog };
        }


        // 4. 모든 검증 성공 (Happy Path)
        validationSuccessful = true;
        console.log("✅ [PoC Success]: 트랜잭션 유효성 및 권한 체크 모두 통과했습니다.");
        return { success: true };

    } catch (error) {
        // 5. 시스템 예외 처리 (최후의 수단으로 Audit Logger 호출)
        const systemError = error instanceof Error ? error.message : "Unknown System Error";
        console.error(`🚨 [System Critical Failure]: ${systemError}`);

        failedAuditLog = await AuditLogger.createFailureAuditBlock(
            "Critical System Exception",
            {
                source_ip: "SYSTEM_FAILURE",
                attempted_user: 'N/A',
                resource_id: attemptedResourceId,
                error_detail: systemError,
                timestamp: new Date().toISOString()
            }
        );

        return { success: false, auditRecord: failedAuditLog };
    } finally {
        console.log("--- [PoC] 트랜잭션 검증 종료 ---\n");
    }
}