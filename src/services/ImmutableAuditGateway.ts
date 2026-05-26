// src/services/ImmutableAuditGateway.ts

import * as crypto from '../utils/crypto'; // SHA-256 hashing utility assumed
import { AuditBlock } from './AuditLogger'; // Assuming AuditBlock structure is defined here or in a shared model

/**
 * @typedef {Object} TransactionPayload - 클라이언트가 제출하는 트랜잭션 페이로드
 * @property {string} transactionId - 고유 거래 ID
 * @property {number} timestamp - 트랜잭션 발생 시간
 * @property {any} data - 실제 트랜잭션 데이터 (예: 사용자 활동 기록, 변경된 권한 등)
 * @property {string} previousBlockHash - 이 블록의 이전 블록 해시 값 (체인 검증용)
 */

/**
 * Immutable Audit Gateway Service. 모든 감사 로직의 단일 진입점(Single Source of Truth).
 * 법적 증명력을 담보하는 트랜잭션 처리 게이트웨이 역할을 수행합니다.
 * @module IAGService
 */
export class ImmutableAuditGateway {

    /**
     * 초기 블록을 생성하거나, 새로운 감사 블록을 생성하는 핵심 로직.
     * @param {TransactionPayload} payload - 검증할 트랜잭션 데이터와 이전 해시.
     * @returns {{block: AuditBlock, success: boolean, message: string}} 결과 객체
     */
    public static submitAuditRequest(payload) {
        // 1. 인증 및 권한 체크 (Mocking TLS/JWT)
        if (!this.mockJwtAuth(payload)) {
            return { block: null, success: false, message: "401 UNAUTHORIZED: Missing or invalid JWT signature/expiry." };
        }

        // 2. 체이닝 해싱 검증 (Chain Validation)
        const currentBlockHash = crypto.calculateHash(payload);
        if (!this.isValidPreviousBlock(payload.previousBlockHash)) {
            return { block: null, success: false, message: "400 BAD REQUEST: Invalid previousBlockHash. Chain integrity compromised." };
        }

        // 3. 트랜잭션 데이터 유효성 검사 (Data Validation)
        if (!this.validateTransactionData(payload)) {
            return { block: null, success: false, message: "422 UNPROCESSABLE ENTITY: Transaction data failed internal validation rules." };
        }

        // 4. 성공적으로 모든 검증을 통과하면 AuditBlock 생성 및 반환
        const newAuditBlock = new AuditBlock(
            payload.data, // 트랜잭션 데이터 자체를 블록에 포함
            payload.timestamp,
            currentBlockHash,
            payload.previousBlockHash
        );

        return { 
            block: newAuditBlock, 
            success: true, 
            message: `200 OK: Audit Block successfully generated and appended to the chain. Hash: ${currentBlockHash}` 
        };
    }

    /**
     * 체이닝 무결성 검증 로직 (가장 중요)
     * @param {string} previousHash - 클라이언트로부터 받은 이전 블록 해시.
     * @returns {boolean} 유효하면 true, 아니면 false.
     */
    private static isValidPreviousBlock(previousHash) {
        // PoC 환경이므로, 특정 더미 값을 검증 기준으로 사용합니다. 
        // 실제로는 DB에서 최신 블록의 해시를 조회해야 합니다.
        const expectedBlockHash = "0000_INITIAL_AUDIT_BLOCK";
        return previousHash === expectedBlockHash;
    }

    /**
     * 트랜잭션 데이터 무결성 검사 (비즈니스 로직 검증)
     * @param {TransactionPayload} payload 
     * @returns {boolean} 유효하면 true, 아니면 false.
     */
    private static validateTransactionData(payload) {
        // 실제로는 TransactionValidator.ts의 복잡한 비즈니스 규칙이 여기에 들어갑니다.
        if (!payload || typeof payload.transactionId !== 'string' || payload.data === undefined) {
            return false;
        }
        console.log(`[Validation Check] Passed for transaction ID: ${payload.transactionId}`);
        return true;
    }

    /**
     * JWT 인증 및 권한 검사 (Mocking)
     * @param {TransactionPayload} payload 
     */
    private static mockJwtAuth(payload) {
        // 실제로는 'Bearer <JWT_TOKEN>'을 추출하여 RS256으로 서명 확인하고, 만료 시간/권한을 체크합니다.
        // PoC에서는 단순히 특정 트랜잭션 ID가 포함되면 유효하다고 가정합니다.
        return payload && payload.transactionId !== "INVALID-AUTH"; 
    }
}

// Exporting for testing and usage
export { ImmutableAuditGateway };