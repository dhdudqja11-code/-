/**
 * @module AuditLogger
 * 시스템의 모든 트랜잭션을 불변적으로 기록하는 핵심 서비스 계층입니다.
 * 체이닝 해싱(Chaining Hashing) 원칙을 준수하여 법적 증명력을 확보합니다.
 */

import { AuditBlock } from './models';
// 가정: 실제 SHA256 해시 생성 라이브러리 (예: crypto/sha256) 사용
import * as CryptoHash from '../utils/crypto'; 

/**
 * 감사 로그 기록기 클래스 (Audit Logger)
 * 모든 트랜잭션은 이 게이트웨이를 통과해야 합니다.
 */
export class AuditLogger {

    // 시스템 시작 시점의 초기 블록 해시값 (Chain Genesis Block)
    private static GENESIS_HASH: string = "0" + ".".repeat(64); 

    /**
     * 새로운 감사 블록을 생성하고, 이전 블록과의 무결성을 검증합니다.
     * @param lastBlockHash - 데이터베이스에서 가져온 직전 트랜잭션의 blockHash.
     * @param transactionDetails - 현재 기록할 원본 트랜잭션 상세 정보.
     * @returns 새로 생성된 AuditBlock 객체 (블록체인 체인이 완성됨).
     */
    public async createNewAuditBlock(lastBlockHash: string, transactionDetails: Record<string, any>): Promise<AuditBlock> {
        console.log(`[AuditLogger] Initiating new audit block creation... Previous Hash: ${lastBlockHash}`);

        // 1. 트랜잭션 데이터의 고유 해시 생성 (Payload Hashing)
        const payload = this.serializeTransaction(transactionDetails);
        const payloadHash = CryptoHash.calculateSha256(payload);

        // 2. 블록을 구성할 원본 문자열 준비: [Previous Hash][Payload Hash][Timestamp]
        const timestamp = new Date().toISOString();
        const sourceString = `${lastBlockHash}:${payloadHash}:${timestamp}`;

        // 3. 최종 블록 해시 계산 (체이닝)
        const blockHash = CryptoHash.calculateSha256(sourceString);
        console.log(`[AuditLogger] Block Hash Calculated: ${blockHash}`);

        // 4. 불변 감사 블록 생성 및 반환
        const newBlock: AuditBlock = {
            previousHash: lastBlockHash,
            transactionData: {
                serviceId: transactionDetails.sourceService || 'UNKNOWN',
                action: transactionDetails.action || 'N/A',
                payloadHash: payloadHash,
                details: transactionDetails,
            },
            blockHash: blockHash,
            timestamp: timestamp,
        };

        // TODO: 이 newBlock을 영구 저장소(DB)에 원자적 트랜잭션으로 기록해야 합니다. 
        // DB 쓰기 성공 시, 해당 blockHash가 다음 요청의 lastBlockHash가 됩니다.
        console.log(`[AuditLogger] Audit Block successfully generated and ready for persistent storage.`);

        return newBlock;
    }


    /**
     * 트랜잭션 데이터를 표준화된 문자열 형식으로 직렬화합니다 (Deterministic Serialization).
     * @param details - 기록할 원본 데이터.
     * @returns 해시 계산에 사용될 표준 JSON 문자열.
     */
    private serializeTransaction(details: Record<string, any>): string {
        // 순서가 중요하므로, 객체를 정렬된 키로 JSON 문자열화하여 결정론적 출력을 보장합니다.
        const sortedKeys = Object.keys(details).sort();
        let jsonString = "{";
        sortedKeys.forEach((key, index) => {
            jsonString += `"${key}": "${details[key]}",`;
            if (index < sortedKeys.length - 1) jsonString += ", ";
        });
        jsonString = jsonString.slice(0, -2) + "}"; // 마지막 쉼표 제거
        return JSON.stringify(details);
    }

    /**
     * 시스템 초기화 시점의 체인 시작 지점을 확인합니다.
     */
    public static getGenesisBlockHash(): string {
        return AuditLogger.GENESIS_HASH;
    }
}