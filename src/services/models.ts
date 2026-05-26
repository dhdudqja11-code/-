/**
 * @module models 
 * 서비스 계층에서 사용되는 공통 데이터 모델 정의.
 */

import { JwtPayload } from 'jsonwebtoken'; // 가정: jsonwebtoken 라이브러리 사용
import { CryptoHash } from '../utils/crypto'; // 가정: 해시 유틸리티 사용

/**
 * 인증 토큰의 페이로드 구조 (JWT Payload)
 * @param userId - 사용자 고유 ID
 * @param role - 시스템 권한 레벨 ('ADMIN', 'USER', 'GUEST')
 * @param issuedAt - 토큰 발급 시간 (ISO 8601 String)
 */
export interface JwtPayload {
    userId: string;
    role: 'ADMIN' | 'STAFF' | 'CLIENT';
    iat: string; // Issued At
}

/**
 * 원격 제어 시스템의 모든 트랜잭션 기록을 위한 불변 블록 구조.
 * 이 모델이 바로 체인(Chain)을 형성합니다.
 */
export interface AuditBlock {
    // 1. 이전 블록의 해시값 (무결성 검증의 핵심). 이것이 곧 '체인'입니다.
    previousHash: string;
    
    // 2. 이 블록에 기록되는 트랜잭션 데이터의 요약 및 구조화된 페이로드.
    transactionData: {
        serviceId: string; // 어떤 서비스에서 발생했는지 (e.g., 'RemoteControl', 'Payment')
        action: string;    // 수행된 행위 (e.g., 'COMMAND_EXECUTION', 'STATE_CHANGE')
        payloadHash: string; // 페이로드 자체의 해시값
        details: Record<string, any>; // 실제 트랜잭션 상세 데이터
    };

    // 3. 이 블록 자체를 고유하게 식별하는 최종 해시값. 모든 것을 포함합니다.
    blockHash: string;
    
    // 4. 기록 시점의 타임스탬프 (추가적인 법적 증거 자료).
    timestamp: string; 
}

/**
 * API 요청에 사용될 인증 정보 모델
 */
export interface AuthRequest {
    username: string;
    password?: string; // 로그인 시만 필요
}