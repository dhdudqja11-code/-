const fs = require('fs');
const path = require('path');
const http = require('http');

// Read stdin
let inputData = '';
process.stdin.on('data', chunk => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    try {
        if (!inputData.trim()) {
            console.error("Error: Empty input payload");
            process.exit(1);
        }
        
        const payload = JSON.parse(inputData);
        const taskId = payload.task_id || 'unknown-task';
        const productName = payload.product_name || 'unknown-product';
        const shortForm = payload.short_form || '';
        const longForm = payload.long_form || '';
        
        // 1. 로컬 역사 저장 처리
        // cwd가 _company 이므로 marketing_history 폴더를 바로 만들어 저장합니다.
        const historyDir = path.join(process.cwd(), 'marketing_history', `release_${taskId}_${Date.now()}`);
        fs.mkdirSync(historyDir, { recursive: true });
        
        fs.writeFileSync(path.join(historyDir, 'short_form.txt'), shortForm, 'utf-8');
        fs.writeFileSync(path.join(historyDir, 'long_form_blog.md'), longForm, 'utf-8');
        
        console.log(`[Local Save] Saved marketing assets in ${historyDir}`);
        
        // 2. 외부 마케팅 게이트웨이 웹훅 송출 처리
        const webhookPayload = JSON.stringify({
            id: `release_${taskId}`,
            kind: 'marketing_release',
            payload: payload,
            approvedAt: new Date().toISOString()
        });
        
        // FastAPI 서버 포트를 감안하여 127.0.0.1:8000 에 송출을 시도합니다.
        const options = {
            hostname: '127.0.0.1',
            port: 8000,
            path: '/api/v1/marketing/webhook',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(webhookPayload)
            },
            timeout: 5000
        };
        
        const req = http.request(options, res => {
            let resData = '';
            res.on('data', d => resData += d);
            res.on('end', () => {
                console.log(`[Webhook Dispatch] Status: ${res.statusCode}`);
                console.log(`[Webhook Dispatch] Response: ${resData}`);
                process.exit(0);
            });
        });
        
        req.on('error', error => {
            console.error(`[Webhook Dispatch Error] ${error.message}`);
            // 테스트나 로컬 오프라인 시 서버가 구동 중이지 않을 수도 있으므로,
            // 로컬 파일 저장은 완료되었기 때문에 warning을 주고 정상 완료(exit 0) 처리하여 무결성을 보장합니다.
            console.log("(Note: Webhook gateway offline, local copy successfully persisted)");
            process.exit(0);
        });
        
        req.write(webhookPayload);
        req.end();
        
    } catch (err) {
        console.error(`Executor Exception: ${err.message}`);
        process.exit(1);
    }
});
