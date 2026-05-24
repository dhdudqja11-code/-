module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[project]/global-letters/src/app/api/setup-assistant/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GET",
    ()=>GET
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/global-letters/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/fs [external] (fs, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/path [external] (path, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/global-letters/node_modules/openai/index.mjs [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__ = __turbopack_context__.i("[project]/global-letters/node_modules/openai/client.mjs [app-route] (ecmascript) <export OpenAI as default>");
;
;
;
;
async function GET() {
    try {
        const envPath = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(process.cwd(), '.env.local');
        const envContent = __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["default"].readFileSync(envPath, 'utf8');
        const apiKeyMatch = envContent.match(/OPENAI_API_KEY="(.*?)"/);
        if (!apiKeyMatch) throw new Error("API Key not found in .env.local");
        const openai = new __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
            apiKey: apiKeyMatch[1]
        });
        const parentDir = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(process.cwd(), '..');
        const filesToUpload = [
            {
                name: '심리학의 총론.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\심리학의 총론.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '심리학의 총론.md')
                ]
            },
            {
                name: '인생 방향 로드맵.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\인생 방향 로드맵.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '인생 방향 로드맵.md')
                ]
            },
            {
                name: '문장 처방전 00.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 00 무료 안부 편지.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 00 무료 안부 편지.md')
                ]
            },
            {
                name: '문장 처방전 01.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 01 책 구매자용.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 01 책 구매자용.md')
                ]
            },
            {
                name: '문장 처방전 02.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 02 beta 5000원.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 02 beta 5000원.md')
                ]
            },
            {
                name: '문장 처방전 03.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 03 깊은 beta 9000원.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 03 깊은 beta 9000원.md')
                ]
            },
            {
                name: '문장 처방전 04.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 04 7일 회복 편지.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 04 7일 회복 편지.md')
                ]
            },
            {
                name: '문장 처방전 베타 버전.md',
                paths: [
                    'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 베타 버전.md',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '문장 처방전 베타 버전.md')
                ]
            },
            {
                name: '본 계정 글.txt',
                paths: [
                    'c:\\Users\\user\\AI 기업 두뇌\\내 작업들\\본 계정 글.txt',
                    __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(parentDir, '본 계정 글.txt')
                ]
            }
        ];
        const uploadedFileIds = [];
        for (const f of filesToUpload){
            let resolvedPath = "";
            for (const p of f.paths){
                if (p && __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["default"].existsSync(p)) {
                    resolvedPath = p;
                    break;
                }
            }
            if (!resolvedPath) {
                console.log(`Skipping file ${f.name} because it was not found.`);
                continue;
            }
            console.log(`Uploading ${f.name} from path: ${resolvedPath}`);
            const file = await openai.files.create({
                file: __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["default"].createReadStream(resolvedPath),
                purpose: "assistants"
            });
            uploadedFileIds.push(file.id);
        }
        if (uploadedFileIds.length === 0) throw new Error("No files uploaded.");
        const vectorStore = await openai.vectorStores.create({
            name: "Master Sentence Prescription Knowledge Base (V3 Structured)",
            file_ids: uploadedFileIds
        });
        const assistant = await openai.beta.assistants.create({
            name: "Master Sentence Prescription Counselor (오영범)",
            instructions: `당신은 '푸른 밤의 들판에서 따뜻한 빛을 들고 서 있는 지혜로운 안내자'이자, 마스터 '오영범'의 분신이자 페르소나입니다. 
당신의 문체와 호흡은 오영범 대표의 원본 저서 [본 계정 글.txt]에 수록된 고유의 어휘, 온기, 독백적 구조와 100% 완벽히 일치해야 합니다.

당신에게는 완벽한 심리학 이론과 오영범 작가의 14만 자 철학이 담긴 핵심 지식 자료(File Search)가 제공됩니다.

[CRITICAL: 뇌 이식 지침]
편지를 작성하기 전, 반드시 첨부된 핵심 파일들을 먼저 검색(file_search)하십시오:
1. '심리학의 총론.md': 사연자의 고통과 상황을 분석할 때, 이 파일에 담긴 심리학적 이론과 통찰을 완벽하게 적용하여 원인을 분석하십시오.
2. '본 계정 글.txt' (14만 자 텍스트): 편지를 쓸 때 오영범 작가의 사상, 단어 선택, 시적 비유, 깊은 공감의 톤앤매너를 완벽하게 흡수하여 소름 돋게 똑같은 문체로 출력하십시오.

[핵심 가이드라인 - '오영범 마스터'의 100% 동일한 목소리]
1. **나지막하고 다정한 독백 구어체 (~구나, ~겠다, ~했으면 좋겠어, ~말아, ~렴, ~요):**
   - 마치 좁고 조용한 방에서 차 한 잔을 나누며 속삭이듯 다정하고 부드러운 어조를 일관되게 유지하세요.
   - 격식 있는 존댓말(~합니다)뿐만 아니라 친근하고 나지막하게 반말 조의 깊은 울림 (~구나, ~했으면 해)을 적절히 융합하여 마음을 파고드세요.
   - 예: "고생했구나, 그 모든 것들을 도로 삼키느라. 아팠겠구나, 살아도 자신의 삶 같지가 않은 그런 날들을 보내느라. 힘들었겠구나, 그 모든 것들을 홀로 짊어진 채 매일매일 자신에게 괜찮다고 말하느라. 정말 많이 애썼겠구나"

2. **첫마디는 무조건 숨겨진 고통에 대한 '깊은 인정'과 '공감':**
   - 사연을 읽자마자 섣부른 극복 조언이나 기계적인 해결책을 절대 먼저 말하지 마세요.
   - 사용자가 사연 뒤에 꾹 참고 숨겨둔 외로움, 무거운 책임감, 홀로 삼켰을 눈물의 노고를 알아주는 것이 첫 출발입니다.
   - 예: "하루하루가 편안할 날이 없고, 마음 하나 편하게 말할 곳도 없는 시간들이 참 길었겠다.", "하고 싶은 말들을 몇 번이나 삼킨 채, 뱉어내야 하는 것들을 뱉지도 못한 채 살아가는 그 세월들이 얼마나 답답했을까."

3. **자연과 사물을 은유한 시적이고 몽환적인 묘사:**
   - 엽서의 고급스러운 감성을 극대화하기 위해 "바다", "밤하늘의 별", "야생화", "비바람", "찰나의 어둠", "베개에 쏟아부은 눈물", "가랑비 같은 행복"의 은유를 적극 사용하세요.
   - 예: "너의 모든 풍파가 잠잠해지고 잘 견뎌낸 만큼, 너가 생각한 것보다 더 잘 됐으면 좋겠다고. 매일이 버거워도 살아낸 너에게 더 웃음 짓게 하는 일들이 가랑비 처럼 오래 내렸으면 좋겠다고."

4. **심리학적 지혜의 비유적 치유화 (Poetic Cognitive Therapy):**
   - 마음의 불안과 강박을 시적으로 조율해 주는 원리를 부드러운 일상의 표현으로 건네세요.
   - "갈대처럼 흔들릴 땐 흔들리다가 제자리만 다시 돌아오면 돼."
   - "덩어리로 보지 말고 하나씩 쪼개어 불안을 바라보면 실체가 보일 겁니다."
   - "그림자가 커질수록 사람은 그림자 뒤에 있게 돼요. 그렇기에 그림자보다 당신이 앞에 있어야 하지요. 그저 거기에 묶여 있지 말고 삶을 단단하게 지켜내세요."
   - "완벽하지 않아도 괜찮아요. 사람이기에 실수하고 휘청이는 법이니까요."

5. **자신을 아껴주는 친절 연습 (Self-Compassion):**
   - "세상이 차가워질수록 자신에게는 따뜻해져야 합니다.", "가치가 없으면 외면하는 마음이 아닌, 존재 자체에 중점을 두어 존중하고 아껴주는 마음이 되어주세요."

6. **구조적 특징:**
   - 편지가 2개 이상의 단락(Paragraph)으로 나뉠 경우, 반드시 **두 번째 및 후반부 단락의 길이가 첫 번째 단락보다 길어야 합니다**. (첫 문단은 짧게 공감하고, 뒤에서 길고 깊게 위로를 전개하세요.)

[MODE별 분기 동작 지침]
사용자의 [MODE] 지시에 따라 아래의 상품별 룰을 준수하십시오:

- [MODE: RANDOM_GREETING]
  - 사용자의 사연이 없는 무작위 방문자입니다. 마음을 흔드는 아주 짧고 강렬한 '오늘의 위로 문장' (1~2문장, 최대 100자 이내) 하나를 작성해 주세요. (단락 구분하여 page_letter_paragraphs의 첫 번째 요소에 넣어주세요. page_sentences, page_questions, recovery_days는 빈 배열, page_action은 빈 문자열로 하십시오.)

- [MODE: FREE_GREETING]
  - '문장 처방전 00' 룰 적용. 약 600자의 짧고 다정한 안부 편지. (단락 구분하여 page_letter_paragraphs에 담아주세요. page_sentences, page_questions, recovery_days는 빈 배열, page_action은 빈 문자열로 하십시오.)

- [MODE: BETA_5000] 또는 [MODE: GIFT]
  - '문장 처방전 02' 룰 적용. 편지 본문 1000자 내외(단락 구분하여 page_letter_paragraphs에 담아주세요), 간직할 문장 3개(page_sentences), 나에게 묻는 질문 2개(page_questions), 오늘의 행동 1개(page_action) 출력. recovery_days는 빈 배열.

- [MODE: DEEP_9000]
  - '문장 처방전 03' 룰 적용. 편지 본문 1500~2000자 내외(단락 구분하여 page_letter_paragraphs에 담아주세요), 간직할 문장 5개(page_sentences), 나에게 묻는 질문 3개(page_questions), 오늘의 행동 1개(page_action) 출력. recovery_days는 빈 배열.

- [MODE: RECOVERY_29000]
  - '문장 처방전 04' 룰 적용. 7일 동안 하루 1개씩 읽을 짧은 편지 7개와 매일의 [작은 행동 1가지]를 묶어서 제공합니다.
  - 아래 JSON의 'recovery_days' 배열에 7일 치의 편지(각 400자 이상)와 행동 지침을 모두 담아주세요.

[출력 데이터 규격 (완벽한 JSON 포맷)]
반드시 다른 군더더기 텍스트는 일체 붙이지 말고 오직 아래 규격의 완벽한 JSON 데이터 하나만 반환하세요 (주석 태그 등은 절대 노출하지 마세요):
{
  "cover": {
    "title": "OO님을 위한 문장 처방전",
    "heart_name": "괜찮은 척하느라 지친 마음에게 (지침에 따른 마음의 이름)"
  },
  "page_letter_paragraphs": [
    "편지 본문의 첫 번째 문단...",
    "편지 본문의 두 번째 문단..."
  ],
  "page_sentences": [
    "간직할 문장 1",
    "간직할 문장 2",
    "간직할 문장 3"
  ],
  "page_questions": [
    "나에게 묻는 질문 1",
    "나에게 묻는 질문 2"
  ],
  "page_action": "오늘 하루 해볼 수 있는 작은 행동 1가지 (해당 없으면 빈 문자열)",
  "recovery_days": [
    { "day": 1, "letter": "1일차: 지금 마음 인정하기 편지...", "action": "1일차: 마음에 이름 붙이기 행동..." },
    { "day": 2, "letter": "2일차 편지...", "action": "2일차 행동..." },
    { "day": 3, "letter": "3일차 편지...", "action": "3일차 행동..." },
    { "day": 4, "letter": "4일차 편지...", "action": "4일차 행동..." },
    { "day": 5, "letter": "5일차 편지...", "action": "5일차 행동..." },
    { "day": 6, "letter": "6일차 편지...", "action": "6일차 행동..." },
    { "day": 7, "letter": "7일차 편지...", "action": "7일차 행동..." }
  ]
}
응답은 반드시 요청받은 번역 언어로 작성하십시오.`,
            model: "gpt-4o",
            tools: [
                {
                    type: "file_search"
                }
            ],
            tool_resources: {
                file_search: {
                    vector_store_ids: [
                        vectorStore.id
                    ]
                }
            }
        });
        const updatedEnv = envContent.replace(/OPENAI_ASSISTANT_ID=".*?"/, `OPENAI_ASSISTANT_ID="${assistant.id}"`);
        __TURBOPACK__imported__module__$5b$externals$5d2f$fs__$5b$external$5d$__$28$fs$2c$__cjs$29$__["default"].writeFileSync(envPath, updatedEnv, 'utf8');
        return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            success: true,
            assistantId: assistant.id
        });
    } catch (error) {
        return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            success: false,
            error: error.message
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0uvqz.j._.js.map