module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

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
"[project]/global-letters/src/app/api/generate-letter/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/global-letters/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/global-letters/node_modules/openai/index.mjs [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__ = __turbopack_context__.i("[project]/global-letters/node_modules/openai/client.mjs [app-route] (ecmascript) <export OpenAI as default>");
;
;
// OpenAI client initialization
const openai = new __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
    apiKey: process.env.OPENAI_API_KEY || ""
});
// Simple in-memory rate limiting store (Works for basic serverless protection)
const rateLimitMap = new Map();
const RATE_LIMIT_MAX = 3; // 하루 무료 제한 횟수
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours
async function POST(req) {
    try {
        const { story, productType, language = "ko" } = await req.json();
        // 1. Get user IP for rate limiting
        const forwardedFor = req.headers.get("x-forwarded-for");
        const ip = forwardedFor ? forwardedFor.split(",")[0] : "unknown-ip";
        // 2. Rate Limiting Logic (Only apply to FREE/RANDOM tier)
        if (productType === "free" || productType === "random") {
            const now = Date.now();
            const userLimit = rateLimitMap.get(ip) || {
                count: 0,
                lastReset: now
            };
            if (now - userLimit.lastReset > RATE_LIMIT_WINDOW_MS) {
                userLimit.count = 0;
                userLimit.lastReset = now;
            }
            if (userLimit.count >= RATE_LIMIT_MAX) {
                return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                    error: "일일 무료 이용 횟수를 초과했습니다. 유료 처방전을 이용해 보세요!"
                }, {
                    status: 429
                });
            }
            userLimit.count += 1;
            rateLimitMap.set(ip, userLimit);
        }
        if (!story && productType !== "random") {
            return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: "Story is required"
            }, {
                status: 400
            });
        }
        const assistantId = process.env.OPENAI_ASSISTANT_ID;
        if (assistantId && assistantId !== "") {
            console.log(`Using Master Assistant for ${productType} tier...`);
            const thread = await openai.beta.threads.create();
            let modePrompt = "";
            switch(productType){
                case "random":
                    modePrompt = `[MODE: RANDOM_GREETING] 사용자의 사연 없이 오늘의 안부를 생성해줘.`;
                    break;
                case "free":
                    modePrompt = `[MODE: FREE_GREETING] 사용자의 사연을 바탕으로 무료 안부를 생성해줘. Story: ${story}`;
                    break;
                case "beta":
                    modePrompt = `[MODE: BETA_5000] 사용자의 사연을 바탕으로 5,000원 상당의 문장 처방전을 생성해줘. Story: ${story}`;
                    break;
                case "deep":
                    modePrompt = `[MODE: DEEP_9000] 사용자의 사연을 바탕으로 9,000원 상당의 깊은 문장 처방전을 생성해줘. Story: ${story}`;
                    break;
                case "recovery":
                    modePrompt = `[MODE: RECOVERY_29000] 사용자의 사연을 바탕으로 29,000원 상당의 7일 회복 편지 패키지를 생성해줘. Story: ${story}`;
                    break;
                default:
                    modePrompt = `[MODE: FREE_GREETING] Story: ${story}`;
            }
            // 글로벌 다국어 번역 시스템 주입 (사용자의 브라우저 언어 감지 적용)
            modePrompt += `\n\n[CRITICAL: MULTI-LANGUAGE TRANSLATION]\nThe user's browser language code is '${language}'. You MUST translate and write the ENTIRE JSON response (including cover title, paragraphs, sentences, questions, action, and recovery_days) in this requested language. Do NOT use Korean unless the language code is 'ko'.`;
            await openai.beta.threads.messages.create(thread.id, {
                role: "user",
                content: modePrompt
            });
            let run = await openai.beta.threads.runs.createAndPoll(thread.id, {
                assistant_id: assistantId
            });
            if (run.status === 'completed') {
                const messages = await openai.beta.threads.messages.list(run.thread_id);
                const lastMessage = messages.data.filter((m)=>m.role === 'assistant')[0];
                if (lastMessage && lastMessage.content[0].type === 'text') {
                    const rawText = lastMessage.content[0].text.value;
                    const cleanText = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
                    const parsedResponse = JSON.parse(cleanText);
                    // 🔒 OpenAI Citation Source Tag 제거 필터 (객체 내 모든 문자열 재귀 필터링)
                    const filterCitations = (obj)=>{
                        for(const key in obj){
                            if (typeof obj[key] === 'string') {
                                obj[key] = obj[key].replace(/【[^】]+】/g, "").trim();
                            } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                                filterCitations(obj[key]);
                            }
                        }
                    };
                    filterCitations(parsedResponse);
                    // 🛡️ API Level defensive post-processing to guarantee 100% strict compliance
                    if (!parsedResponse.cover || typeof parsedResponse.cover !== 'object') {
                        parsedResponse.cover = {};
                    }
                    if (typeof parsedResponse.cover.title !== 'string') {
                        parsedResponse.cover.title = "당신을 위한 문장 처방전";
                    }
                    if (typeof parsedResponse.cover.heart_name !== 'string') {
                        parsedResponse.cover.heart_name = "소중한 마음에게";
                    }
                    if (!Array.isArray(parsedResponse.page_letter_paragraphs)) {
                        parsedResponse.page_letter_paragraphs = typeof parsedResponse.letter === 'string' && parsedResponse.letter.trim() !== '' ? [
                            parsedResponse.letter
                        ] : [
                            "따뜻한 위로의 편지가 작성 중입니다."
                        ];
                    }
                    if (!Array.isArray(parsedResponse.page_sentences)) {
                        parsedResponse.page_sentences = [];
                    }
                    if (!Array.isArray(parsedResponse.page_questions)) {
                        parsedResponse.page_questions = [];
                    }
                    if (typeof parsedResponse.page_action !== 'string') {
                        parsedResponse.page_action = "";
                    }
                    if (!Array.isArray(parsedResponse.recovery_days)) {
                        parsedResponse.recovery_days = [];
                    }
                    const targetSentences = productType === "beta" ? 3 : productType === "deep" ? 5 : 0;
                    const targetQuestions = productType === "beta" ? 2 : productType === "deep" ? 3 : 0;
                    if (targetSentences > 0) {
                        while(parsedResponse.page_sentences.length < targetSentences){
                            parsedResponse.page_sentences.push("가장 당신다운 호흡으로, 오늘 하루를 조용히 채워나가길 바랄게요.");
                        }
                        if (parsedResponse.page_sentences.length > targetSentences) {
                            parsedResponse.page_sentences = parsedResponse.page_sentences.slice(0, targetSentences);
                        }
                    }
                    if (targetQuestions > 0) {
                        while(parsedResponse.page_questions.length < targetQuestions){
                            parsedResponse.page_questions.push("오늘 밤 침대에 눕기 전, 내 마음의 날씨는 어떤 단어로 표현할 수 있을까요?");
                        }
                        if (parsedResponse.page_questions.length > targetQuestions) {
                            parsedResponse.page_questions = parsedResponse.page_questions.slice(0, targetQuestions);
                        }
                    }
                    return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(parsedResponse);
                }
            }
        }
        // Fallback if no Assistant ID is found
        return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: "시스템 설정 중입니다. 잠시 후 다시 시도해 주세요."
        }, {
            status: 503
        });
    } catch (error) {
        console.error("Letter generation error:", error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$global$2d$letters$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: "Failed to generate letter. Please try again later."
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__11rraxt._.js.map