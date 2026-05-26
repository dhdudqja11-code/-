/**
 * @module CryptoHash
 * 암호화 및 해싱 관련 유틸리티 함수 모음.
 * 모든 민감 정보 처리 시 표준 SHA-256을 사용합니다.
 */

// Node.js의 내장 'crypto' 모듈을 사용하는 것을 가정합니다.
import * as crypto from 'crypto'; 

/**
 * 주어진 문자열 데이터를 SHA-256 해시로 계산합니다.
 * @param data - 해싱할 원본 데이터 (문자열).
 * @returns 64자 길이의 16진수 문자열 형태의 해시값.
 */
export class CryptoHash {
    /**
     * SHA-256 기반의 암호화 해시를 계산합니다.
     * 이 함수는 블록체인 체인의 무결성 검증에 사용됩니다.
     * @param data - 원본 데이터 문자열 (Deterministic String).
     * @returns 계산된 해시값.
     */
    public static calculateSha256(data: string): string {
        // UTF-8 인코딩을 명시하여 모든 환경에서 일관성을 유지합니다.
        return crypto.createHash('sha256')
                     .update(data, 'utf8')
                     .digest('hex');
    }

    /**
     * 간단한 무결성 체크를 위한 더미 함수 (실제로는 복잡한 검증 로직 필요).
     */
    public static verifyIntegrity(blockHash: string, expectedHash: string): boolean {
        return blockHash === expectedHash;
    }
}