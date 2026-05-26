import express, { Request, Response, NextFunction } from 'express';
import { IncomingPayload, AnalysisResult, AuditLogEntry, GatewayResponse } from './types';

// --- [ MOCK: 감사 로그 기록 서비스 (Immutable Log Service) ] ---
/**
 * 실제로는 데이터베이스(예: Blockchain Ledger 또는 Write-Once Storage)에 연결되는 비동기 함수입니다.
 * 핵심 원칙: 이 함수는 트랜잭션의 성공 여부와 무관하게, 입력/출력 데이터를 영구적으로 기록해야 합니다.
 * @param entry - 감사 로그로 기록할 최종 데이터 구조체.
 */
const recordAuditLog = async (entry: AuditLogEntry): Promise<boolean> => {
    console.log("🚨 [AUDIT LOGGING SERVICE] Attempting to persist immutable log...");
    // TODO: 실제 DB 연결 및 트랜잭션 커밋 로직 구현
    // 이 부분이 실패하면, 반드시 에러를 던지거나 복구 메커니즘을 가동해야 합니다.
    console.log(`✅ [AUDIT LOGGING SERVICE] Logged successfully for ID: ${entry.log_id}`);
    return true; // 모의 성공 반환
};

// --- [ Middleware: 게이트웨이 핵심 로직 ] ---
/**
 * 모든 요청에 적용되는 전역 게이트웨이 미들웨어입니다.
 * 이 미들웨어는 모든 API 호출을 가로채어 로그 기록을 강제합니다.
 */
const auditGatewayMiddleware = async (req: Request, res: Response, next: NextFunction) => {
    // 1. 트랜잭션 ID 생성 및 초기 로깅 데이터 준비
    const transactionId = crypto.randomUUID(); // UUID 사용 권장
    console.log(`\n--- [GATEWAY] Starting new transaction: ${transactionId} ---`);

    // 요청 본문 파싱 (실제로는 Body-parser가 처리하지만, 명시적으로 가정)
    const incomingPayload: IncomingPayload = {
        source: req.headers['x-client-source'] || 'unknown', // 커스텀 헤더에서 출처 확보 시도
        user_id: req.query.user_id as string | undefined,
        data: req.body as Record<string, any>
    };

    // 2. 요청을 다음 핸들러로 전달 (핵심 비즈니스 로직 실행)
    try {
        // 여기서 next()를 호출하여 실제 Mini ROI 분석기 등의 핵심 서비스가 동작하게 합니다.
        await next(); // Next Function은 async/await 처리가 까다로우므로, 여기서는 요청 객체에 트랜잭션 ID와 Payload를 임시로 부착하는 방식으로 구조화합니다.

        // 🚨 NOTE: Middleware 내에서 next() 호출 후 응답을 받는 것은 복잡하므로,
        // Gateway 자체가 비즈니스 로직을 감싸는 패턴(Wrapper)으로 구현하는 것이 가장 안정적입니다.
        // 일단은 다음 라우터가 실행된 후의 결과를 가정하고 구조를 작성하겠습니다.

    } catch (error: any) {
        const failureResult: AnalysisResult = {
            status: 'FAILURE',
            timestamp_utc: new Date().toISOString(),
            problem_definition: `요청 처리 중 예상치 못한 에러 발생: ${error.message}`,
            cause_analysis: `Gateway에서 Catch됨. 스택 트레이스 분석 필요.`,
            mitigation_suggestion: '클라이언트 측에서 재시도하거나 관리자에게 문의하세요.',
            raw_data: { error: error.toString() }
        };

        const failureLogEntry: AuditLogEntry = {
            log_id: transactionId,
            timestamp: new Date().toISOString(),
            status: 'FAILURE',
            input_payload: incomingPayload,
            output_result: failureResult,
            is_immutable: true
        };

        // 3. 실패 로그 기록 시도 (이 부분은 반드시 실행되어야 함)
        await recordAuditLog(failureLogEntry);

        return res.status(500).json({ success: false, message: "Gateway 내부 오류 발생", data: failureResult });
    }
};


// --- [ API Gateway 라우터 ] ---
const setupApiGateway = (app: express.Express) => {
    // /api/v1/:endpoint는 모든 핵심 기능을 감싸는 게이트웨이입니다.
    app.use('/api/v1', require('express').Router());

    // 실제 로직을 처리하는 메인 핸들러 함수를 만듭니다.
    const roiAnalysisHandler = async (req: Request, res: Response) => {
        const transactionId = crypto.randomUUID();
        console.log(`\n--- [GATEWAY] Processing ROI Analysis for ID: ${transactionId} ---`);

        // 1. 입력 데이터 수집 및 유효성 검증 (Validation Layer)
        const incomingPayload: IncomingPayload = {
            source: 'web-client', // 여기서는 클라이언트가 직접 호출한다고 가정
            user_id: req.query.user_id as string | undefined,
            data: req.body as Record<string, any>
        };

        // 2. 핵심 비즈니스 로직 실행 (Mock)
        try {
             // TODO: 실제 Mini ROI 분석기 모듈을 호출합니다. (예: await miniRoiService.analyze(incomingPayload.data))
            const mockAnalysisResult: AnalysisResult = {
                status: 'SUCCESS',
                timestamp_utc: new Date().toISOString(),
                problem_definition: "데이터 누락으로 인한 법적 책임 위험이 감지되었습니다.",
                cause_analysis: "Source: API Call (2026-05-26). Time: 14:30 KST. 개인정보 필드 A가 미포함됨.",
                mitigation_suggestion: "필수 데이터셋 X, Y를 추가 수집하여 재분석을 권장합니다.",
                raw_data: incomingPayload.data
            };

            // 3. 감사 로그 기록 (Critical Step)
            const successLogEntry: AuditLogEntry = {
                log_id: transactionId,
                timestamp: new Date().toISOString(),
                status: 'SUCCESS',
                input_payload: incomingPayload,
                output_result: mockAnalysisResult,
                is_immutable: true
            };

            await recordAuditLog(successLogEntry); // 반드시 성공 로그를 기록합니다.

            // 4. 클라이언트 응답 (Response)
            return res.status(200).json({ success: true, data: mockAnalysisResult });

        } catch (error: any) {
             // 5. 실패 로직 처리 및 감사 로그 기록
            const failureResult: AnalysisResult = {
                status: 'FAILURE',
                timestamp_utc: new Date().toISOString(),
                problem_definition: `분석 과정에서 치명적인 오류 발생: ${error.message}`,
                cause_analysis: '내부 서버 로직 실패 (Internal Service Failure).',
                mitigation_suggestion: '시스템 관리자에게 문의하여 재점검이 필요합니다.',
                raw_data: {}
            };

            const failureLogEntry: AuditLogEntry = {
                log_id: transactionId,
                timestamp: new Date().toISOString(),
                status: 'FAILURE',
                input_payload: incomingPayload,
                output_result: failureResult,
                is_immutable: true
            };

            await recordAuditLog(failureLogEntry); // 실패 로그도 반드시 기록합니다.

            return res.status(500).json({ success: false, message: "분석 서비스 내부 오류", data: failureResult });
        }
    };

    // 실제 게이트웨이 미들웨어와 핸들러를 결합하여 사용합니다.
    app.get('/roi-analyze', auditGatewayMiddleware, roiAnalysisHandler);
};


export default setupApiGateway;