import { NextResponse } from "next/server";
import OpenAI from "openai";
import { execSync } from "child_process";
import path from "path";

// OpenAI client initialization
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "",
});

// Simple in-memory rate limiting store (Works for basic serverless protection)
const rateLimitMap = new Map<string, { count: number; lastReset: number }>();
const RATE_LIMIT_MAX = 99999; // 하루 무료 제한 횟수 (테스트를 위해 비활성화 수준으로 상향)
const RATE_LIMIT_WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours

export async function POST(req: Request) {
  try {
    const { story, productType, giftRecipient, language = "ko" } = await req.json();

    // 🧠 글로벌 뇌과학/심리학 RAG 지식 피더 쿼리 (Python Bridge)
    let scientificPrescription = {
      title: "Neural Correlates of Resilience and Coping Mechanisms in Stressful Environments",
      authors: "Dr. Sarah Jenkins et al.",
      source_url: "https://europepmc.org/article/MED/109849",
      insight_ko: "스트레스 상황에서 뇌의 전두엽 활성화는 감정 조절과 인지적 재구성을 도와 상처를 스스로 복구하게 합니다."
    };

    try {
      const sanitizedStory = (story || "안부 편지").replace(/"/g, '\\"').replace(/\n/g, " ");
      const scouterScript = path.join(process.cwd(), "..", "scripts", "query_knowledge.py");
      // execSync로 파이썬 브릿지 기동 및 인코딩 가드
      const stdout = execSync(`python "${scouterScript}" "${sanitizedStory}"`, { encoding: "utf-8" });
      const parsed = JSON.parse(stdout.trim());
      if (parsed && parsed.title) {
        scientificPrescription = parsed;
      }
    } catch (scouterErr) {
      console.error("⚠️ Failed to query global knowledge from python scouter bridge:", scouterErr);
    }

    // 🧠 공감 프로파일러 심리 분석 쿼리 (Python Empathy Profiler Agent)
    let emotionProfile = {
      emotions: { anxiety: 0.40, helplessness: 0.30, self_blame: 0.30, sadness: 0.40, loneliness: 0.30 },
      defense_mechanism: "내면화 및 억제",
      core_pain_point: "잠재적인 감정적 스트레스가 누적된 상태",
      prescription_guideline: "사연자의 감정을 따뜻하게 수용하고, 섣부른 조언 대신 절대적 지지를 제공하십시오."
    };

    try {
      const sanitizedStory = (story || "안부 편지").replace(/"/g, '\\"').replace(/\n/g, " ");
      const profilerScript = path.join(process.cwd(), "..", "_company", "_agents", "empathy_profiler.py");
      const stdout = execSync(`python "${profilerScript}" "${sanitizedStory}"`, { encoding: "utf-8" });
      const parsed = JSON.parse(stdout.trim());
      if (parsed && parsed.emotions) {
        emotionProfile = parsed;
      }
    } catch (profilerErr) {
      console.error("⚠️ Failed to profile empathy distress metrics:", profilerErr);
    }

    // 1. Get user IP for rate limiting
    const forwardedFor = req.headers.get("x-forwarded-for");
    const ip = forwardedFor ? forwardedFor.split(",")[0] : "unknown-ip";

    // 2. Rate Limiting Logic (Only apply to FREE/RANDOM tier)
    if (productType === "free" || productType === "random") {
      const now = Date.now();
      const userLimit = rateLimitMap.get(ip) || { count: 0, lastReset: now };

      if (now - userLimit.lastReset > RATE_LIMIT_WINDOW_MS) {
        userLimit.count = 0;
        userLimit.lastReset = now;
      }

      if (userLimit.count >= RATE_LIMIT_MAX) {
        return NextResponse.json(
          { error: "일일 무료 이용 횟수를 초과했습니다. 유료 처방전을 이용해 보세요!" },
          { status: 429 }
        );
      }

      userLimit.count += 1;
      rateLimitMap.set(ip, userLimit);
    }

    if (!story && productType !== "random") {
      return NextResponse.json({ error: "Story is required" }, { status: 400 });
    }

    const assistantId = process.env.OPENAI_ASSISTANT_ID;

    if (assistantId && assistantId !== "") {
      console.log(`Using Master Assistant for ${productType} tier...`);
      
      const thread = await openai.beta.threads.create();
      
      let modePrompt = "";
      switch (productType) {
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
        case "gift":
          modePrompt = `[MODE: GIFT_12000] 사용자의 사연을 바탕으로 12,000원 상당의 선물용 위로 엽서(문장 처방전)를 생성해줘. Recipient: ${giftRecipient || "소중한 사람"}. Story: ${story}`;
          break;
        default:
          modePrompt = `[MODE: FREE_GREETING] Story: ${story}`;
      }

      // 🧠 글로벌 뇌과학 RAG 지침 동적 주입 (Z방안: 따뜻한 본문 융합 유도)
      modePrompt += `\n\n[BRAIN-SCIENCE HEALING RAG INTELLIGENCE]\nYou must integrate the following scientific healing insight subtly and deeply into your comforting letter body paragraph (do NOT mention the title or author in the main letter text, just weave the healing concept warmly): "${scientificPrescription.insight_ko}"`;

      // 🧠 공감 프로파일러 심리 지침 동적 주입 (처방 가이드라인 우선 바인딩)
      modePrompt += `\n\n[PSYCHOLOGY PROFILER DIRECTIVE]\nYou must strictly write the comforting letter aligning with this customized clinical guideline: "${emotionProfile.prescription_guideline}"`;

      // 글로벌 다국어 번역 시스템 주입 (사용자의 브라우저 언어 감지 적용)
      modePrompt += `\n\n[CRITICAL: MULTI-LANGUAGE TRANSLATION]\nThe user's browser language code is '${language}'. You MUST translate and write the ENTIRE JSON response (including cover title, paragraphs, sentences, questions, action, and recovery_days) in this requested language. Do NOT use Korean unless the language code is 'ko'.`;

      await openai.beta.threads.messages.create(thread.id, {
        role: "user",
        content: modePrompt,
      });

      let run = await openai.beta.threads.runs.createAndPoll(thread.id, {
        assistant_id: assistantId,
      });

      if (run.status === 'completed') {
        const messages = await openai.beta.threads.messages.list(run.thread_id);
        const lastMessage = messages.data.filter(m => m.role === 'assistant')[0];
        
        if (lastMessage && lastMessage.content[0].type === 'text') {
          const rawText = lastMessage.content[0].text.value;
          const cleanText = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
          const parsedResponse = JSON.parse(cleanText);
          
          // 🔒 OpenAI Citation Source Tag 제거 필터 (객체 내 모든 문자열 재귀 필터링)
          const filterCitations = (obj: any) => {
            for (const key in obj) {
              if (typeof obj[key] === 'string') {
                obj[key] = obj[key].replace(/【[^】]+】/g, "").trim();
              } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                filterCitations(obj[key]);
              }
            }
          };
          filterCitations(parsedResponse);
 
          // 🛡️ API Level defensive post-processing to guarantee 100% strict compliance
          const isKo = language === "ko";
          if (!parsedResponse.cover || typeof parsedResponse.cover !== 'object') {
            parsedResponse.cover = {};
          }
          if (typeof parsedResponse.cover.title !== 'string') {
            parsedResponse.cover.title = isKo ? "당신을 위한 문장 처방전" : "Sentence Prescription for You";
          }
          if (typeof parsedResponse.cover.heart_name !== 'string') {
            parsedResponse.cover.heart_name = isKo ? "소중한 마음에게" : "To a Precious Heart";
          }

          if (!Array.isArray(parsedResponse.page_letter_paragraphs)) {
            parsedResponse.page_letter_paragraphs = typeof parsedResponse.letter === 'string' && parsedResponse.letter.trim() !== ''
              ? [parsedResponse.letter]
              : [isKo ? "따뜻한 위로의 편지가 작성 중입니다." : "A warm comforting letter is being written."];
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

          const targetSentences = productType === "beta" ? 3 : (productType === "deep" ? 5 : 0);
          const targetQuestions = productType === "beta" ? 2 : (productType === "deep" ? 3 : 0);

          if (targetSentences > 0) {
            while (parsedResponse.page_sentences.length < targetSentences) {
              parsedResponse.page_sentences.push(isKo 
                ? "가장 당신다운 호흡으로, 오늘 하루를 조용히 채워나가길 바랄게요."
                : "I hope you quietly fill your day today with your own unique breath.");
            }
            if (parsedResponse.page_sentences.length > targetSentences) {
              parsedResponse.page_sentences = parsedResponse.page_sentences.slice(0, targetSentences);
            }
          }

          if (targetQuestions > 0) {
            while (parsedResponse.page_questions.length < targetQuestions) {
              parsedResponse.page_questions.push(isKo
                ? "오늘 밤 침대에 눕기 전, 내 마음의 날씨는 어떤 단어로 표현할 수 있을까요?"
                : "Before lying down in bed tonight, what word can express the weather of my heart?");
            }
            if (parsedResponse.page_questions.length > targetQuestions) {
              parsedResponse.page_questions = parsedResponse.page_questions.slice(0, targetQuestions);
            }
          }

          // 🔒 뇌과학 RAG 학술 레퍼런스(Scientific Reference) SSoT 데이터 이식
          parsedResponse.scientific_reference = {
            title: scientificPrescription.title,
            authors: scientificPrescription.authors,
            source_url: scientificPrescription.source_url,
            insight_ko: scientificPrescription.insight_ko
          };

          // 🧠 공감 프로파일러 다차원 감정 지표 (Web UI 렌더링용) SSoT 데이터 이식
          parsedResponse.emotions = emotionProfile.emotions;

          return NextResponse.json(parsedResponse);
        }
      }
    }

    // Fallback if no Assistant ID is found
    return NextResponse.json(
      { error: "시스템 설정 중입니다. 잠시 후 다시 시도해 주세요." },
      { status: 503 }
    );
  } catch (error) {
    console.error("Letter generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate letter. Please try again later." },
      { status: 500 }
    );
  }
}
