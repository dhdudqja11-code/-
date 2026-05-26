import type { AuditLog } from "../types";

/**
 * @description 불변 감사 로그를 생성하고 체이닝 해싱을 적용하는 핵심 서비스.
 * 이 모듈은 시스템의 '진실의 원천(Single Source of Truth)' 역할을 수행합니다.
 */
export class AuditLogService {
    private readonly LOG_STORE: Map<string, AuditLog> = new Map();

    /**
     * @description 이전 로그 블록을 가져와서 트랜잭션에 대한 고유 해시를 계산하고 새 로그를 기록합니다.
     * @param transactionData - 감사할 데이터 (Payload).
     * @returns 성공적으로 기록된 AuditLog 객체.
     */
    public async recordTransaction(transactionData: any): Promise<AuditLog> {
        // 1. 이전 해시값 가져오기 (없으면 초기 마스터 해시 사용)
        const lastLog = this.getLatestLog();
        const previousHash = lastLog ? lastLog.currentBlockHash : "0".repeat(64); // Genesis Hash

        // 2. 새로운 트랜잭션 데이터와 이전 해시를 조합하여 입력 문자열 생성
        const dataToHash = `${transactionData.timestamp}|${JSON.stringify(transactionData)}`;
        
        // 3. SHA-256 체이닝 해싱 적용 (핵심 로직)
        // Node.js 환경에서 crypto 모듈 사용 가정
        const currentHash = await this.calculateBlockHash(previousHash, dataToHash);

        // 4. 최종 로그 객체 생성 및 저장
        const newLog: AuditLog = {
            transactionId: transactionData.transactionId || Date.now().toString(),
            timestamp: transactionData.timestamp || new Date().toISOString(),
            sourceModule: 'RemoteControl',
            callingUserId: transactionData.callingUserId || 'UNKNOWN',
            sessionContextHash: transactionData.sessionContextHash || 'N/A',
            previousBlockHash: previousHash, // 이전 해시 기록
            dataPayloadSummary: transactionData.payloadSummary || {}, 
            resultStatus: transactionData.status || 'PENDING',
            currentBlockHash: currentHash // 현재 블록의 고유 해시값
        };

        this.LOG_STORE.set(newLog.transactionId, newLog);
        console.log(`✅ Audit Log Recorded Successfully. New Hash: ${currentHash}`);
        return newLog;
    }

    /**
     * @description 가장 최근에 기록된 로그 블록을 검색합니다.
     */
    private getLatestLog(): ?AuditLog {
        if (this.LOG_STORE.size === 0) return null;
        // Map은 삽입 순서를 보장하므로, 마지막 항목이 최신이다 가정
        return this.LOG_STORE.values().next().value as AuditLog | undefined;
    }

    /**
     * @description SHA-256 해싱을 시뮬레이션합니다. (실제로는 Node의 crypto 모듈 사용)
     * @private
     */
    private async calculateBlockHash(previousHash: string, dataToHash: string): Promise<string> {
        // 실제 환경에서는 'crypto' 모듈과 비동기 연산이 필요함. 
        // 여기서는 시뮬레이션을 위해 임시 해시를 반환합니다.
        const combinedString = previousHash + dataToHash;
        console.log(`[DEBUG] Hashing Input: ${combinedString}`);
        return `SHA256_${Math.random().toString(36).substring(2, 10).toUpperCase()}_${Date.now()}`;
    }
}

export type AuditLog = {
    transactionId: string;
    timestamp: string;
    sourceModule: 'RemoteControl';
    callingUserId: string;
    sessionContextHash: string;
    previousBlockHash: string; 
    dataPayloadSummary: any;
    resultStatus: 'SUCCESS' | 'FAILURE' | 'WARNING';
    currentBlockHash: string;
}