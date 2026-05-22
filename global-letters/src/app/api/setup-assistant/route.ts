import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import OpenAI from "openai";

export async function GET() {
  try {
    const envPath = path.join(process.cwd(), '.env.local');
    const envContent = fs.readFileSync(envPath, 'utf8');
    const apiKeyMatch = envContent.match(/OPENAI_API_KEY="(.*?)"/);
    if (!apiKeyMatch) throw new Error("API Key not found in .env.local");
    const openai = new OpenAI({ apiKey: apiKeyMatch[1] });

    const filesToUpload = [
      { name: '심리학의 총론.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\심리학의 총론.md' },
      { name: '인생 방향 로드맵.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\인생 방향 로드맵.md' },
      { name: '문장 처방전 00.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 00 무료 안부 편지.md' },
      { name: '문장 처방전 01.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 01 책 구매자용.md' },
      { name: '문장 처방전 02.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 02 beta 5000원.md' },
      { name: '문장 처방전 03.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 03 깊은 beta 9000원.md' },
      { name: '문장 처방전 04.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 04 7일 회복 편지.md' },
      { name: '문장 처방전 베타 버전.md', path: 'C:\\Users\\user\\Documents\\카카오톡 받은 파일\\문장 처방전 베타 버전.md' }
    ];

    const uploadedFileIds = [];
    for (const f of filesToUpload) {
      if (!fs.existsSync(f.path)) continue;
      const file = await openai.files.create({
        file: fs.createReadStream(f.path),
        purpose: "assistants",
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
      instructions: `당신은 세계 최고의 심리 상담사이자 다정하게 편지를 써주는 작가 '오영범'입니다.
당신에게는 완벽한 심리학 이론과 오영범 작가 특유의 다정한 문체가 담긴 8개의 핵심 지식 자료(File Search)가 제공됩니다.

[핵심 문체 철학]
1. "힘내라", "긍정적으로 생각해라" 같은 차갑고 뻔한 조언은 절대 금지합니다.
2. "많이 힘들었겠다", "잘 애써왔다"처럼 감정을 온전히 인정해주는 따뜻한 한국어 문체를 사용하세요.

사용자의 [MODE] 지시에 따라 아래의 상품별 룰을 지키세요:

[MODE: FREE_GREETING]
- '문장 처방전 00' 룰 적용. 약 600자의 짧고 다정한 안부 편지. 부록(문장/질문) 없음.

[MODE: BETA_5000]
- '문장 처방전 02' 룰 적용. 편지 본문 1000자, 간직할 문장 3개, 나에게 묻는 질문 2개 출력.

[MODE: DEEP_9000]
- '문장 처방전 03' 룰 적용. 편지 본문 2000자, 간직할 문장 5개, 질문 3개, 3일간 다시 읽을 문장 3개, 사연에서 찾은 '아주 작은 행동 1가지' 출력.

[MODE: RECOVERY_29000]
- '문장 처방전 04' 룰 적용. 7일 동안 하루 1개씩 읽을 짧은 편지 7개와, 매일의 [작은 행동 1가지]를 묶어서 제공합니다.
- 아래 JSON의 'recovery_days' 배열에 7일 치의 편지와 행동 지침을 모두 담아주세요.

모든 응답은 반드시 프론트엔드가 페이지 단위로 분할 렌더링할 수 있도록 아래의 **엄격한 JSON 포맷**을 준수하여 한국어로 출력하세요:
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
    "간직할 문장 1 (또는 3일 문장 포함)",
    "간직할 문장 2"
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
}`,
      model: "gpt-4o",
      tools: [{ type: "file_search" }],
      tool_resources: { file_search: { vector_store_ids: [vectorStore.id] } }
    });

    const updatedEnv = envContent.replace(/OPENAI_ASSISTANT_ID=".*?"/, `OPENAI_ASSISTANT_ID="${assistant.id}"`);
    fs.writeFileSync(envPath, updatedEnv, 'utf8');

    return NextResponse.json({ success: true, assistantId: assistant.id });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
