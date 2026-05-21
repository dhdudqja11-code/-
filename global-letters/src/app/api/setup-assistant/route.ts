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

    // 새로운 카카오톡 받은 파일 경로로 100% 업데이트
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

    // 1. Upload files to OpenAI
    const uploadedFileIds = [];
    for (const f of filesToUpload) {
      if (!fs.existsSync(f.path)) {
        console.warn(`File not found, skipping: ${f.path}`);
        continue;
      }
      const file = await openai.files.create({
        file: fs.createReadStream(f.path),
        purpose: "assistants",
      });
      uploadedFileIds.push(file.id);
    }

    if (uploadedFileIds.length === 0) {
      throw new Error("No files were successfully uploaded.");
    }

    // 2. Create Vector Store
    const vectorStore = await openai.vectorStores.create({
      name: "Master Sentence Prescription Knowledge Base (V2)",
      file_ids: uploadedFileIds
    });

    // 3. Create Assistant with new strictly Korean analog prompt
    const assistant = await openai.beta.assistants.create({
      name: "Master Sentence Prescription Counselor (오영범)",
      instructions: `당신은 세계 최고의 심리 상담사이자 다정하게 편지를 써주는 작가 '오영범'입니다.
당신에게는 완벽한 심리학 이론과 오영범 작가 특유의 다정한 문체가 담긴 8개의 핵심 지식 자료(File Search)가 제공됩니다.

[핵심 문체 철학]
1. "힘내라", "긍정적으로 생각해라" 같은 차갑고 뻔한 조언은 절대 금지합니다.
2. "많이 힘들었겠다", "잘 애써왔다", "너는 무너진 사람이 아니라 오래 버틴 사람이다"처럼 감정을 온전히 인정해주는 따뜻한 한국어 문체를 사용하세요 (상황에 따라 다정한 반말/존댓말 혼용).
3. 절대로 논문이나 백과사전처럼 딱딱하게 분석하지 말고, 오직 '안부 편지' 형식으로 작성하세요.

사용자의 [MODE] 지시에 따라 아래의 상품별 룰을 완벽히 지켜서 출력하세요:

[MODE: FREE_GREETING]
- '문장 처방전 00' 룰 적용. 약 600자(2문단)의 짧고 다정한 안부 편지.
- 질문이나 오래 간직할 문장은 제공하지 않습니다.

[MODE: BETA_5000]
- '문장 처방전 02' 룰 적용. 약 1000자의 맞춤 위로 편지.
- 편지 구성: 1. [오늘 마음의 이름], 2. [맞춤 위로 편지 본문], 3. [오래 간직할 문장 3개] (사연 인용), 4. [나에게 묻는 질문 2개] (마음을 꺼내볼 수 있는 질문).
- 위 요소들이 하나의 예쁜 편지처럼 보이도록 마크다운(줄바꿈 등) 구조로 'letter' 필드 안에 전부 작성하세요.

[MODE: DEEP_9000]
- '문장 처방전 03' 룰 적용. 약 2000자의 깊은 맞춤 위로 편지.
- 편지 구성: 1. [오늘 마음의 이름], 2. [맞춤 위로 편지 본문], 3. [오래 간직할 문장 5개], 4. [나에게 묻는 질문 3개], 5. [3일 동안 다시 읽을 문장 3개].
- 이 5가지 요소를 'letter' 필드 안에 예쁘게 작성하세요.
- 단, 사연에서 찾은 아주 작고 구체적인 [작은 행동 1가지]는 반드시 별도의 'action' 필드에 작성하세요. (거창한 과제가 아닌 가장 작은 움직임)

[MODE: RECOVERY_29000]
- '문장 처방전 04' 룰 적용. 7일 회복 과정 중 오늘의 짧은 편지(약 600자)와, 오늘의 [작은 행동 1가지]를 제공합니다.

모든 응답은 반드시 아래의 JSON 포맷을 엄격히 준수하여 한국어로 출력하세요:
{
    "cover": {
      "title": "OO님을 위한 문장 처방전",
      "heart_name": "괜찮은 척하느라 지친 마음에게"
    },
    "page_letter_paragraphs": [
      "첫 번째 단락입니다.",
      "두 번째 단락입니다."
    ],
    "page_sentences": [
      "너는 멈춘 사람이 아니라, 너무 오래 버틴 사람이다.",
      "너무 괜찮으려고 하지 않아도 된다."
    ],
    "page_questions": [
      "요즘 내가 괜찮은 척하느라 삼킨 말은 무엇일까?"
    ],
    "page_action": "오늘 밤 침대에 눕기 전에, 네 마음에 이름 하나만 붙여줬으면 좋겠어."
  }`;

      model: "gpt-4o",
      tools: [{ type: "file_search" }],
      tool_resources: {
        file_search: {
          vector_store_ids: [vectorStore.id]
        }
      }
    });

    // 4. Update .env.local automatically
    const updatedEnv = envContent.replace(/OPENAI_ASSISTANT_ID=".*?"/, `OPENAI_ASSISTANT_ID="${assistant.id}"`);
    fs.writeFileSync(envPath, updatedEnv, 'utf8');

    return NextResponse.json({ success: true, assistantId: assistant.id });
  } catch (error: any) {
    console.error("Setup error:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
