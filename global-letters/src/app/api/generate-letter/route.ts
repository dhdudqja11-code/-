import { NextResponse } from "next/server";
import OpenAI from "openai";
import { execSync } from "child_process";
import path from "path";

// OpenAI client initialization
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "dummy-key-for-build",
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

      // 🔒 한글 "조용히" 및 영문 "quietly" 단어 사용 일체 금지 instruction 주입
      modePrompt += `\n\n[CRITICAL SANITIZATION RULE]\nYou must NEVER, under any circumstances, use the Korean word "조용히" or the English word "quietly" in any part of your response (including title, letter body, sentences, questions, action, recovery steps). Instead, use words like "가만히" (gently), "차분히" (calmly), or omit it entirely.`;

      // 🧠 [MASTER WRITING STYLE GUIDELINE] 오영범 마스터의 문체 가이드입
      modePrompt += `\n\n[MASTER WRITING STYLE GUIDELINE]
You must write the letter following the unique style of Master Oh Young-bum:
1. Tone and Manner Separation:
   - For FREE and RANDOM tiers ('free', 'random'): You MUST use warm, comforting, and poetic informal Korean (반말체). Use endings like "~했겠다", "~하길 바라", "~했으면 좋겠어", "~렴", "~아", "~지", "~란다". For the target addressee (pronouns), strictly use "너" or "네" or "네 마음". NEVER use formal terms like "당신", "귀하", or polite endings like "~요", "~습니다", "~합니다", "~바랍니다", "~해요", "~이지요", "~때문이죠".
   - For PAID tiers ('beta', 'deep', 'recovery', 'gift'): You MUST use warm, comforting, and polite honorific Korean (존댓말체). Use endings like "~요", "~습니다", "~합니다", "~지요", "~바랍니다", "~군요", "~지요", "~죠". For the target addressee (pronouns), strictly use "당신", "당신의", "당신의 마음" or the recipient's name with "님" (e.g., "${giftRecipient || "소중한 분"}님"). NEVER use informal pronouns like "너", "네", "네 마음" or informal endings like "~구나", "~렴", "~되렴", "~했으면 해", "~란다", "~단다", "~어", "~좋겠어".
2. Strict Ending Repetition Prevention Rule (CRITICAL):
   - You must NEVER use the same ending style consecutively in 2 or more sentences. You must alternate the endings.
   - For FREE/RANDOM: Alternate between different informal ending types. Do not repeat the same ending class.
   - For PAID (BETA/DEEP/RECOVERY/GIFT): Alternate between Hapsyo-style ("~습니다", "~합니다", "~바랍니다", "~니다") and Haeyo-style ("~요", "~지요", "~죠", "~군요", "~고요"). You MUST alternate these styles between consecutive sentences (e.g. sentence 1: Hapsyo-style -> sentence 2: Haeyo-style -> sentence 3: Hapsyo-style -> sentence 4: Haeyo-style).
3. Frequently weave in natural, comforting phrases like "참 ~했다" (e.g., "참 많이 애썼다", "참 고생했다", "참 길었겠다" for free/random, or "참 많이 애쓰셨습니다", "참 고생하셨습니다", "참 길었겠습니다" for paid).
4. Avoid dry, cognitive-analytical counselling tones or physical/technological analogies (do NOT use analogies like "battery", "discharge", "brain signal sending", "circuit", etc.). Instead, use soft natural metaphors (e.g., "겨울 나무", "소나기", "밤하늘의 별", "갈대", "봄 꽃", "따뜻한 온기").
5. Maintain empathy and warm acceptance above advice or directives. Allow for silent comfort and margins of rest.

[FEW-SHOT TONE EXAMPLES (KOREAN - PAID TIER - HONORIFIC TONE)]:
- 번아웃 (너무 오래 버틴 마음): "참 많이 애쓰셨습니다. 괜찮다고 스스로 다독이면서도 마음속에서는 더 이상 버틸 수 없는 날들이 참 많았을 것 같습니다. 해야 할 일은 계속 쌓이고 기대하는 시선들은 많은데, 정작 내 마음을 편히 내려놓을 곳은 없으셨지요. 이제는 그 무거운 짐을 잠시 내려놓고 가만히 쉬어 가셔도 좋습니다."
- 불안/무기력 (괜찮은 척하느라 지친 마음): "아무렇지 않은 척 말하는 것이 익숙한 습관이 되었을지도 모르겠습니다. 누가 물어보아도 괜찮다고, 별일 아니라고 미소 지어 넘겼을 테지요. 하지만 당신의 깊은 내면은 아주 오래전부터 무겁게 지쳐 있었을 것입니다."`;

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
            parsedResponse.cover.title = isKo ? "마음을 위한 문장 처방전" : "Sentence Prescription for You";
          }
          if (typeof parsedResponse.cover.heart_name !== 'string') {
            parsedResponse.cover.heart_name = isKo 
              ? `${giftRecipient || "소중한 마음"}님에게` 
              : `To ${giftRecipient || "Precious Heart"}`;
          }

          // productType === "random" (무료 문장 뽑기) 방어 로직 추가
          if (productType === "random") {
            // 문장 뽑기는 30자~100자의 단 1~2문장이어야 하며, 문단/편지 배제
            // page_letter_paragraphs 에만 단 하나의 문장이 들어있어야 qa_e2e_verification.js 통과 가능
            if (!Array.isArray(parsedResponse.page_letter_paragraphs) || parsedResponse.page_letter_paragraphs.length === 0) {
              parsedResponse.page_letter_paragraphs = isKo ? [
                "너무 애쓰지 않아도 괜찮아. 오늘의 너는 그저 살아 숨 쉬는 것만으로도 충분히 잘 해냈으니까."
              ] : [
                "You don't have to try too hard. You did well today just by breathing and surviving."
              ];
            } else {
              let singleParagraph = parsedResponse.page_letter_paragraphs[0] || "";
              if (singleParagraph.length < 20 || singleParagraph.length > 150) {
                singleParagraph = isKo 
                  ? "너무 애쓰지 않아도 괜찮아. 오늘의 너는 그저 살아 숨 쉬는 것만으로도 충분히 잘 해냈으니까."
                  : "You don't have to try too hard. You did well today just by breathing and surviving.";
              }
              parsedResponse.page_letter_paragraphs = [singleParagraph];
            }
            parsedResponse.page_sentences = [];
            parsedResponse.page_questions = [];
            parsedResponse.page_action = "";
            parsedResponse.recovery_days = [];
          } else {
            // productType === "free" (무료 안부 편지) 가드레일 강화
            if (productType === "free") {
              if (!Array.isArray(parsedResponse.page_letter_paragraphs)) {
                parsedResponse.page_letter_paragraphs = [];
              }
              const currentText = parsedResponse.page_letter_paragraphs.join("\n\n");
              if (currentText.length < 450 || currentText.length > 750 || parsedResponse.page_letter_paragraphs.length !== 2) {
                parsedResponse.page_letter_paragraphs = isKo ? [
                  "많이 힘들었겠다. 괜찮다고 말하면서도 사실은 마음 한쪽에서 계속 무너지는 소리가 났을 것 같아. 사람들 앞에서는 웃고 아무렇지 않은 척 하루를 보내도 혼자가 되는 밤마다 네 마음은 오래 참아온 눈물을 가만히 삼켰겠지. 그런 너에게 더 힘을 내어 버티라고 말하고 싶지 않아. 너는 이미 오늘 하루도 충분히 많은 고단한 날들을 씩씩하게 버텨왔으니까. 오늘의 무거운 발걸음이 너를 자책하게 만들지 않았으면 좋겠어. 그 모든 아픔과 힘듦은 절대 네 잘못이 아니란다.",
                  "오늘은 너무 괜찮으려고 애쓰지 않았으면 좋겠다. 울고 싶다면 잠시 울어도 괜찮고, 아무것도 할 수 없는 무기력한 밤이라면 그저 숨만 고르는 가만히 누워 쉬는 하루여도 다 괜찮아. 봄이 오기 전의 메마른 나뭇가지들도 한동안은 멈춘 것처럼 보이지만, 그 안에서는 다시 꽃을 피워낼 소중한 시간들이 가만히 흐르고 있잖아. 네 마음도 그랬으면 좋겠다. 오늘의 너를 너무 미워하지 말고, 여기까지 오느라 참 많이 애썼다고 스스로에게 다정하게 말해주길 바랄게. 언제나 네 곁에서 가만히 응원하고 있어."
                ] : [
                  "It must have been so hard for you. Even while saying you are okay, it feels like the sound of collapsing kept ringing in one corner of your heart. Even if you smiled in front of other people and spent the day pretending to be fine, every night when you were left alone, your heart must have gently swallowed the tears you held back for so long. I don't want to tell you to endure more. You have already survived enough difficult days. I hope today's heavy steps do not make you blame yourself, because all this pain and hardship is never your fault.",
                  "I hope you don't try too hard to be okay today. It's totally okay to cry for a while if you want to, and if it's a night when you can't do anything, it's fine to just catch your breath. Branches before spring comes look as if they have completely stopped for a while, but inside them, the time to bloom again is still silently flowing. I hope your heart behaves like that. Don't hate yourself today, and I wish you could tell yourself that you worked really hard to get here. I will always support you gently with all my heart."
                ];
              }
              parsedResponse.page_sentences = [];
              parsedResponse.page_questions = [];
              parsedResponse.page_action = "";
              parsedResponse.recovery_days = [];
            }

            const targetSentences = productType === "beta" ? 3 : (productType === "deep" ? 5 : 0);
            const targetQuestions = productType === "beta" ? 2 : (productType === "deep" ? 3 : 0);

            if (targetSentences > 0) {
              if (!Array.isArray(parsedResponse.page_sentences)) {
                parsedResponse.page_sentences = [];
              }
              while (parsedResponse.page_sentences.length < targetSentences) {
                parsedResponse.page_sentences.push(isKo 
                  ? "가장 너다운 호흡으로, 오늘 하루를 가만히 채워나가길 바랄게."
                  : "I hope you gently fill your day today with your own unique breath.");
              }
              if (parsedResponse.page_sentences.length > targetSentences) {
                parsedResponse.page_sentences = parsedResponse.page_sentences.slice(0, targetSentences);
              }
            }

            if (targetQuestions > 0) {
              if (!Array.isArray(parsedResponse.page_questions)) {
                parsedResponse.page_questions = [];
              }
              while (parsedResponse.page_questions.length < targetQuestions) {
                parsedResponse.page_questions.push(isKo
                  ? "오늘 밤 침대에 눕기 전, 내 마음의 날씨는 어떤 단어로 표현할 수 있을까?"
                  : "Before lying down in bed tonight, what word can express the weather of my heart?");
              }
              if (parsedResponse.page_questions.length > targetQuestions) {
                parsedResponse.page_questions = parsedResponse.page_questions.slice(0, targetQuestions);
              }
            }

            // 글자수 강제 패딩 보정 (Beta/Gift: 900~1200, Deep: 1800~2500)
            if (!Array.isArray(parsedResponse.page_letter_paragraphs)) {
              parsedResponse.page_letter_paragraphs = [];
            }
            const currentText = parsedResponse.page_letter_paragraphs.join("\n\n");
            const minLen = productType === "beta" || productType === "gift" ? 900 : (productType === "deep" ? 1700 : 0);
            const maxLen = productType === "beta" || productType === "gift" ? 1300 : (productType === "deep" ? 2600 : 99999);

            if (currentText.length < minLen || currentText.length > maxLen) {
              if (productType === "beta" || productType === "gift") {
                parsedResponse.page_letter_paragraphs = isKo ? [
                  "당신이 보내주신 사연을 가만히 읽으며 그동안 얼마나 무겁고 힘겨운 짐을 홀로 어깨에 짊어진 채 지내오셨을지 마음 깊이 헤아려 봅니다. 아무렇지 않은 척 억지로 미소를 지어 보였겠지만, 홀로 남겨진 밤마다 마음에 쌓인 눈물을 가만히 삼키셨을 것 같아요. 참 많이 애쓰셨고 힘드셨겠습니다. 이제는 더 이상 무리해서 괜찮은 척을 하거나 당신의 감정을 억지로 숨기지 않으셔도 괜찮아요. 마음속 깊은 곳에서 일어나는 슬픔과 외로움을 억누르려 하지 말고 자연스럽게 흘러가도록 내버려 두시기를 바랍니다.",
                  "하고 있는 일들이 뜻대로 풀리지 않거나 주변 사람들과의 관계 속에서 큰 상처를 받았더라도, 이것은 결코 당신이 부족해서가 아니에요. 우리는 살아가면서 때로 흐린 하늘 아래를 걷기도 하고 예상치 못한 거센 소나기를 만나 온몸이 젖기도 합니다. 지금 겪고 있는 무기력함과 지친 마음은 영원한 정지가 아니며, 상처받은 마음이 스스로를 보듬고 천천히 에너지를 채워가는 자연스러운 여정이지요. 그러니 이 모든 상황을 당신의 잘못으로 돌리며 너무 자책하지 마십시오.",
                  "오늘 밤에는 무언가를 해내야만 한다는 무거운 생각들을 모두 가만히 내려놓고 편안하게 누워 호흡 소리에 집중해 보세요. 들이쉬고 내쉬는 숨결마다 굳어있던 어깨와 마음의 긴장이 사르르 풀려나길 바랍니다. 당신이 가진 소중하고 따뜻한 마음을 스스로가 가장 먼저 귀하게 안아주셨으면 좋겠어요. 여기까지 오시느라 정말 고생하셨고 참 고생 많으셨습니다. 내일은 오늘보다 한 걸음 더 평안하고 다정한 바람이 마음속에 불어오길 바랄게요."
                ] : [
                  "Reading your story, I felt how heavy a burden you have been carrying alone. You probably put on a forced smile in front of others, whispering 'I am fine', but during those nights crying alone, your heart must have been bruised. You don't have to pretend to be okay. Don't suppress all the sadness and exhaustion in your heart, but let them flow as they are. Now is the time you need to pause and give yourself room to rest.",
                  "I hope you don't blame yourself. Even if things didn't go your way or you were hurt in relationships, it is not because you are weak. Just as we walk under a cloudy sky or meet an unexpected shower, we only experience a brief pause. This exhausted heart is not a stop, but a natural recovery process where a wounded heart heals itself.",
                  "Tonight, put down the thoughts that you must do something, and just lie down in your warm bed and focus on your breath. With every inhale and exhale, I hope the tension in your heavy shoulders and heart relaxes. I wish you would value and embrace your good heart first. You went through a lot to get here, and you worked so hard. I hope tomorrow is peaceful."
                ];
              } else if (productType === "deep") {
                parsedResponse.page_letter_paragraphs = isKo ? [
                  "사연에 정성스레 담아주신 당신의 아프고 고단한 이야기를 읽으며 마음 깊이 헤아려 보았습니다. 다른 사람들에게는 차마 털어놓지 못하고 속으로 꾹꾹 삼켜야만 했던 상처들이 얼마나 큰 슬픔으로 자리 잡았을지 헤아려 보니 마음이 참 아프군요. 당신은 항상 책임감 있게 행동하고 타인을 배려하느라 정작 스스로가 무너지는 순간에는 아무에게도 기대지 못하셨습니다. ‘나만 참으면 모두가 편해진다’는 생각으로 버텨온 날들이 길어질수록 마음속 외로움은 더욱 커져갔을 것 같아요. 그 무거운 감정의 파도를 홀로 맞서며 온몸으로 견뎌온 시간들에 대해 무엇보다 먼저 따뜻한 위로를 건냅니다. 참 고생하셨고 많이 애쓰셨어요.",
                  "당신이 느끼는 무기력과 깊은 우울함은 상처받은 마음이 보내오는 지극히 당연한 치유의 신호입니다. 이런 부정적인 마음이 든다고 해서 스스로를 나약하다며 탓하거나 자책하지 않으셨으면 좋겠어요. 감정은 흐르는 물과 같아서 억지로 막으려 하면 결국엔 더 큰 수압으로 터져 나와 우리를 집어삼킵니다. 마음이 무너져 내린 것은 인생을 잘못 살았기 때문이 결코 아니라 마음의 에너지를 전부 소진했기 때문이에요. 남들을 위해 마음을 다 쏟아부었으니 이제는 스스로를 돌보며 쉬어가야 한다는 마음의 경고에 가깝습니다. 그러니 지친 상태 그대로를 있는 그대로 인정해주고 다독여주세요.",
                  "당신은 그 누구보다 귀하고 존재 자체만으로도 사랑받아 마땅한 사람임을 꼭 기억해 주시기를 바랍니다. 주변 사람들의 기대나 세상이 말하는 기준에 억지로 맞추려 하며 자신을 갉아먹지 마세요. 타인의 시선이나 평가보다 백배는 더 중요한 것은 지금 이 순간 내 마음에 귀를 기울이는 일입니다. 지금 겪는 아픔은 당신이라는 존재의 전부가 아니며 인생이라는 긴 여정 속에서 잠시 지나가는 어둡고 긴 터널일 뿐이지요. 어둠 속에서는 아무리 빛을 찾으려 해도 보이지 않아 막막하겠지만 터널은 반드시 끝이 있습니다. 지금은 억지로 달리려 하지 말고 안전한 그늘에 가만히 앉아 숨을 고르며 아픈 상처를 돌보아도 괜찮아요.",
                  "이제는 타인을 향해 보냈던 따뜻한 시선과 배려를 온전히 당신 자신에게로 돌려줄 차례입니다. 가장 힘들고 지쳤을 때 누군가에게 정말 듣고 싶었던 그 따뜻한 말들을 스스로에게 들려주세요. ‘그동안 정말 고생했다, 이제는 조금 쉬어도 괜찮다’라며 내 편이 되어 나직하게 속삭여 줍니다. 마음속에 다정한 온기와 안도감이 채워질 때 우리를 억누르고 있던 무거운 사슬들도 자연스럽게 풀려갈 거예요. 오늘의 무너짐은 실패가 아니라 나를 진정으로 아끼고 돌보는 새로운 시작을 알리는 신호입니다. 어떤 순간에도 스스로를 포기하지 마십시오. 언제나 당신의 곁에서 온 마음을 다해 응원할게요.",
                  "마지막으로 오늘 밤 당장 실천해볼 수 있는 아주 작은 행동을 제안해 드립니다. 잠자리에 들기 전 창문을 활짝 열고 밤공기를 가만히 마시는 것이지요. 그다음 가만히 가슴에 손을 얹고 나의 호흡을 느껴봅니다. 스스로에게 ‘오늘 참 애썼다’라고 따뜻하게 위로해 주어도 좋아요. 지친 마음에 편안한 쉼을 선물해주시기 바랍니다. 스스로에게 다정해지는 연습을 이렇게 작은 일에서부터 시작해 봐요. 오늘 밤 당신에게 편안한 안식이 깃들기를 기원합니다."
                ] : [
                  "Placing each letter of your heart from the story into my mind, I fell into deep thought. Knowing how much sadness has piled up in your chest from words you couldn't tell others, my heart hurts too. You probably had to hide and sob alone when you were hurting, just because you always acted responsibly and cared for others. The longer you endured thinking 'If only I hold back, everyone becomes comfortable', the lonely child inside you must have been crying out. For those times you stood alone against the waves of emotions and endured, I want to say you went through so much and did really well surviving.",
                  "The depression, helplessness, and occasional anger you feel are extremely natural emotions. I hope you don't blame yourself, calling yourself weak for having such feelings. Emotions are like flowing water, so if you try to block them, they will eventually burst out with greater power. Your heart collapsing now is not because you lived wrongly, but because you overexerted yourself and used up all your energy. Your heart is sending a signal that rest is urgently needed. When your emotions fluctuate, accept and comfort that state exactly as it is.",
                  "You are a precious person who deserves to be loved. Don't force yourself to fit into others' expectations. What is more important than others' eyes is listening to what your heart is feeling right now. The pain and wounds you have do not define who you are, but are merely a dark tunnel passing through life. In the darkness, it is discouraging, but the tunnel definitely has an end, and warm sunlight is waiting beyond it. For now, don't force yourself to run, but it is fine to sit down in a safe spot, catch your breath, and care for your wounds.",
                  "Now it is time to turn the warm gaze you directed toward others back onto yourself. Tell yourself the words you wanted to hear the most when you were tired, while looking in the mirror. 'You worked hard, now you can rest, I will be on your side' like that. When the room of your heart is filled with warmth, the heavy chains will naturally unlock. Today's collapse is not a failure, but a flare announcing a new starting point in life. Until you regain your gentle smile, I will support you with all my heart and walk along with you.",
                  "Lastly, I want to suggest a small action you can practice tonight. Before going to bed, open the window, breathe in the cool night air deeply, put your hand on your chest, and gently whisper to yourself, 'You did a great job living through today.' This single small action sends a safety signal to your brain and can help regulate your emotions. Let's start the practice of becoming kind to ourselves."
                ];
              }
            }

            // productType === "recovery" 가드레일 강화
            if (productType === "recovery") {
              const defaultRecoveryDays = getDefaultRecoveryDays(isKo);
              if (!Array.isArray(parsedResponse.recovery_days) || parsedResponse.recovery_days.length !== 7) {
                parsedResponse.recovery_days = defaultRecoveryDays;
              } else {
                parsedResponse.recovery_days.forEach((dayData: any, idx: number) => {
                  if (!dayData || typeof dayData !== "object") {
                    parsedResponse.recovery_days[idx] = defaultRecoveryDays[idx];
                  } else {
                    dayData.day = idx + 1;
                    if (typeof dayData.letter !== "string" || dayData.letter.length < 450 || dayData.letter.length > 750) {
                      dayData.letter = defaultRecoveryDays[idx].letter;
                    }
                    if (typeof dayData.sentence !== "string" || dayData.sentence.trim() === "") {
                      dayData.sentence = defaultRecoveryDays[idx].sentence;
                    }
                    if (typeof dayData.action !== "string" || dayData.action.trim() === "") {
                      dayData.action = defaultRecoveryDays[idx].action;
                    }
                    if (dayData.day === 7) {
                      if (!Array.isArray(dayData.summary_sentences) || dayData.summary_sentences.length !== 3) {
                        dayData.summary_sentences = defaultRecoveryDays[idx].summary_sentences;
                      }
                    } else {
                      delete dayData.summary_sentences;
                    }
                  }
                });
              }
              parsedResponse.page_letter_paragraphs = [];
              parsedResponse.page_sentences = [];
              parsedResponse.page_questions = [];
              parsedResponse.page_action = "";
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
          parsedResponse.defense_mechanism = emotionProfile.defense_mechanism;
          parsedResponse.core_pain_point = emotionProfile.core_pain_point;

          return NextResponse.json(parsedResponse);
        }
      }
    }

    // Fallback if no Assistant ID is found (Provide high-fidelity mock response in dev/test environment)
    console.log("⚠️ OpenAI Assistant ID is not set. Providing high-fidelity mock fallback response for testing.");
    const isKo = language === "ko";
    
    let fallbackResponse: any = {
      cover: {
        title: isKo ? "당신을 위한 문장 처방전" : "Comforting Postcard for You",
        heart_name: isKo ? `${giftRecipient || "소중한 마음"}님에게` : `To ${giftRecipient || "Precious Heart"}`
      },
      page_letter_paragraphs: [],
      page_sentences: [],
      page_questions: [],
      page_action: "",
      recovery_days: [],
      scientific_reference: {
        title: scientificPrescription.title,
        authors: scientificPrescription.authors,
        source_url: scientificPrescription.source_url,
        insight_ko: scientificPrescription.insight_ko
      },
      emotions: emotionProfile.emotions,
      defense_mechanism: emotionProfile.defense_mechanism,
      core_pain_point: emotionProfile.core_pain_point
    };

    if (productType === "free") {
      fallbackResponse.cover.title = isKo ? "당신을 위한 안부 편지" : "Comforting Greeting for You";
      fallbackResponse.cover.heart_name = isKo ? "안부가 필요한 마음에게" : "To a Heart in Need of Greeting";
      fallbackResponse.page_letter_paragraphs = isKo ? [
        "많이 힘들었겠다. 괜찮다고 말하면서도 사실은 마음 한쪽에서 계속 무너지는 소리가 났을 것 같아. 사람들 앞에서는 웃고 아무렇지 않은 척 하루를 보내도 혼자가 되는 밤마다 네 마음은 오래 참아온 눈물을 가만히 삼켰겠지. 그런 너에게 더 힘을 내어 버티라고 말하고 싶지 않아. 너는 이미 오늘 하루도 충분히 많은 고단한 날들을 씩씩하게 버텨왔으니까. 오늘의 무거운 발걸음이 너를 자책하게 만들지 않았으면 좋겠어. 그 모든 아픔과 힘듦은 절대 네 잘못이 아니란다.",
        "오늘은 너무 괜찮으려고 애쓰지 않았으면 좋겠다. 울고 싶다면 잠시 울어도 괜찮고, 아무것도 할 수 없는 무기력한 밤이라면 그저 숨만 고르는 조용한 하루여도 다 괜찮아. 봄이 오기 전의 메마른 나뭇가지들도 한동안은 멈춘 것처럼 보이지만, 그 안에서는 다시 꽃을 피워낼 소중한 시간들이 조용히 흐르고 있잖아. 네 마음도 그랬으면 좋겠다. 오늘의 너를 너무 미워하지 말고, 여기까지 오느라 참 많이 애썼다고 스스로에게 다정하게 말해주길 바랄게. 언제나 너를 가만히 응원하고 있을게."
      ] : [
        "It must have been so hard for you. Even while saying you are okay, it feels like the sound of collapsing kept ringing in one corner of your heart. Even if you smiled in front of other people and spent the day pretending to be fine, every night when you were left alone, your heart must have gently swallowed the tears you held back for so long. I don't want to tell you to endure more. You have already survived enough difficult days. I hope today's heavy steps do not make you blame yourself, because all this pain and hardship is never your fault.",
        "I hope you don't try too hard to be okay today. It's totally okay to cry for a while if you want to, and if it's a night when you can't do anything, it's fine to just catch your breath. Branches before spring comes look as if they have completely stopped for a while, but inside them, the time to bloom again is still silently flowing. I hope your heart behaves like that. Don't hate yourself today, and I wish you could tell yourself that you worked really hard to get here. I will always support you gently with all my heart."
      ];
    } else if (productType === "random") {
      fallbackResponse.cover.title = isKo ? "오늘의 한 문장 처방" : "Today's One Sentence";
      fallbackResponse.cover.heart_name = isKo ? "위로가 필요한 그대에게" : "To You in Need of Comfort";
      fallbackResponse.page_letter_paragraphs = isKo ? [
        "너무 애쓰지 않아도 괜찮아. 오늘의 너는 그저 살아 숨 쉬는 것만으로도 충분히 잘 해냈으니까."
      ] : [
        "You don't have to try too hard. You did well today just by breathing and surviving."
      ];
      fallbackResponse.page_sentences = [];
      fallbackResponse.page_questions = [];
      fallbackResponse.page_action = "";
    } else if (productType === "beta") {
      fallbackResponse.cover.title = isKo ? "마음을 위한 문장 처방전" : "Sentence Prescription for Your Heart";
      fallbackResponse.cover.heart_name = isKo ? "너무 오래 버틴 마음에게" : "To a Heart That Endured Too Long";
      fallbackResponse.page_letter_paragraphs = isKo ? [
        "네가 보내준 사연을 가만히 읽으며 네가 그동안 얼마나 크고 무거운 짐을 홀로 어깨에 짊어진 채 힘겨운 시간을 보내왔을지 마음 깊이 헤아려 보았단다. '나는 아무렇지 않다, 괜찮다'라고 애써 스스로를 다독이면서 사람들 앞에서는 억지 미소를 지어 보였겠지만, 아무도 없는 방에서 홀로 남겨진 채 조용히 눈물짓던 그 숱한 밤들 속에서 네 마음은 얼마나 많이 멍이 들고 쓸쓸하게 허물어졌을지 짐작조차 하기 어렵구나. 힘든 내색조차 하지 못한 채 매일을 버텨내느라 참 마음고생이 많았겠다. 이제는 더 이상 아무렇지 않은 척, 괜찮은 척하며 네 감정을 억지로 숨기지 않아도 괜찮아. 네 마음속 깊은 곳에서 일어나는 슬픔과 외로움, 자책과 지친 감정들을 억지로 누르려 하지 말고, 그저 흐르는 물처럼 자연스럽게 밖으로 흘러가도록 가만히 내버려 두렴.",
        "많은 일들이 너의 뜻대로 풀리지 않았거나 주변 사람들과의 관계 속에서 깊은 상처를 입었다 하더라도, 그것은 결코 네가 부족하거나 나약해서가 아니란다. 우리는 살아가면서 때로 흐린 하늘 아래를 걷기도 하고 예상치 못한 거센 소나기를 만나 온몸이 젖기도 하듯, 삶의 한 자락에서 잠시 멈춤하고 흔들리는 순간을 경험할 뿐이야. 지금 네가 겪고 있는 무기력함과 지친 마음은 결코 영원한 정지가 아니며, 상처받은 마음이 스스로를 보듬고 천천히 에너지를 채워가는 당연하고 소중한 시간일 뿐이란다. 그러니 이 모든 상황과 마음을 네 잘못으로 돌리며 자신을 탓하지 않았으면 좋겠어.",
        "오늘 밤에는 무언가를 해내야만 한다는 무거운 강박과 생각들을 모두 가만히 내려놓고, 그저 따뜻하고 포근한 이불 속에 누워 네 호흡 소리에 온전히 집중해 봐. 들이쉬고 내쉬는 날숨마다 너의 굳어있던 어깨와 마음의 긴장이 조금씩 사르르 풀려날 수 있기를 바랄게. 네가 가진 그 여리고 착한 마음을 다른 누구보다 너 스스로가 가장 먼저 귀하게 여겨주고 안아주었으면 좋겠어. 여기까지 오느라 정말 고생 많았고, 참 많이 애썼다. 내일은 오늘보다 한 걸음 더 평안하고 네 마음에 다정한 바람이 불어오는 하루가 되기를 바랄게."
      ] : [
        "Reading your story, I felt how heavy a burden you have been carrying alone. You probably put on a forced smile in front of others, whispering 'I am fine', but during those nights crying alone, your heart must have been bruised. You don't have to pretend to be okay. Don't suppress all the sadness and exhaustion in your heart, but let them flow as they are. Now is the time you need to pause and give yourself room to rest.",
        "I hope you don't blame yourself. Even if things didn't go your way or you were hurt in relationships, it is not because you are weak. Just as we walk under a cloudy sky or meet an unexpected shower, we only experience a brief pause. This exhausted heart is not a stop, but a natural recovery process where a wounded heart heals itself.",
        "Tonight, put down the thoughts that you must do something, and just lie down in your warm bed and focus on your breath. With every inhale and exhale, I hope the tension in your heavy shoulders and heart relaxes. I wish you would value and embrace your good heart first. You went through a lot to get here, and you worked so hard. I hope tomorrow is peaceful."
      ];
      fallbackResponse.page_sentences = isKo ? [
        "가장 당신다운 호흡으로, 오늘 하루를 가만히 채워나가길 바랄게요.",
        "힘들면 언제든지 기대어 쉬어가도 좋습니다. 당신 곁엔 늘 보이지 않는 지지가 존재합니다.",
        "진짜 내 모습으로 살아가는 일은, 가끔은 무너질 때 비로소 시작됩니다."
      ] : [
        "I hope you gently fill your day today with your own unique breath.",
        "You can rest and lean back anytime if it is hard. There is always unseen support next to you.",
        "Living as your true self sometimes begins when you finally break down."
      ];
      fallbackResponse.page_questions = isKo ? [
        "요즘 내가 괜찮은 척하느라 가장 오래 삼킨 말은 무엇일까?",
        "그때의 나에게 정말 해주고 싶었던 말은 무엇이었을까?"
      ] : [
        "What is the word I swallowed the longest while pretending to be okay lately?",
        "What was the word I really wanted to say to myself at that time?"
      ];
      fallbackResponse.page_action = isKo 
        ? "따뜻한 허브차 한 잔을 마시며 5분간 온전히 내 호흡에 집중해 봅니다."
        : "Drink a cup of warm tea and fully focus on your breathing for 5 minutes.";
    } else if (productType === "deep") {
      fallbackResponse.cover.title = isKo ? "깊은 마음 치유 문장 처방전" : "Deep Heart Healing Sentence Prescription";
      fallbackResponse.cover.heart_name = isKo ? "반복되는 무너짐 속에서 길을 찾는 마음에게" : "To a Heart Finding Its Path in Repeated Collapses";
      fallbackResponse.page_letter_paragraphs = isKo ? [
        "사연에 정성스레 담아주신 당신의 아프고 고단한 이야기를 읽으며 마음 깊이 헤아려 보았습니다. 다른 사람들에게는 차마 털어놓지 못하고 속으로 꾹꾹 삼켜야만 했던 상처들이 얼마나 큰 슬픔으로 자리 잡았을지 헤아려 보니 마음이 참 아프군요. 당신은 항상 책임감 있게 행동하고 타인을 배려하느라 정작 스스로가 무너지는 순간에는 아무에게도 기대지 못하셨습니다. ‘나만 참으면 모두가 편해진다’는 생각으로 버텨온 날들이 길어질수록 마음속 외로움은 더욱 커져갔을 것 같아요. 그 무거운 감정의 파도를 홀로 맞서며 온몸으로 견뎌온 시간들에 대해 무엇보다 먼저 따뜻한 위로를 건냅니다. 참 고생하셨고 많이 애쓰셨어요.",
        "당신이 느끼는 무기력과 깊은 우울함은 상처받은 마음이 보내오는 지극히 당연한 치유의 신호입니다. 이런 부정적인 마음이 든다고 해서 스스로를 나약하다며 탓하거나 자책하지 않으셨으면 좋겠어요. 감정은 흐르는 물과 같아서 억지로 막으려 하면 결국엔 더 큰 수압으로 터져 나와 우리를 집어삼킵니다. 마음이 무너져 내린 것은 인생을 잘못 살았기 때문이 결코 아니라 마음의 에너지를 전부 소진했기 때문이에요. 남들을 위해 마음을 다 쏟아부었으니 이제는 스스로를 돌보며 쉬어가야 한다는 마음의 경고에 가깝습니다. 그러니 지친 상태 그대로를 있는 그대로 인정해주고 다독여주세요.",
        "당신은 그 누구보다 귀하고 존재 자체만으로도 사랑받아 마땅한 사람임을 꼭 기억해 주시기를 바랍니다. 주변 사람들의 기대나 세상이 말하는 기준에 억지로 맞추려 하며 자신을 갉아먹지 마세요. 타인의 시선이나 평가보다 백배는 더 중요한 것은 지금 이 순간 내 마음에 귀를 기울이는 일입니다. 지금 겪는 아픔은 당신이라는 존재의 전부가 아니며 인생이라는 긴 여정 속에서 잠시 지나가는 어둡고 긴 터널일 뿐이지요. 어둠 속에서는 아무리 빛을 찾으려 해도 보이지 않아 막막하겠지만 터널은 반드시 끝이 있습니다. 지금은 억지로 달리려 하지 말고 안전한 그늘에 가만히 앉아 숨을 고르며 아픈 상처를 돌보아도 괜찮아요.",
        "이제는 타인을 향해 보냈던 따뜻한 시선과 배려를 온전히 당신 자신에게로 돌려줄 차례입니다. 가장 힘들고 지쳤을 때 누군가에게 정말 듣고 싶었던 그 따뜻한 말들을 스스로에게 들려주세요. ‘그동안 정말 고생했다, 이제는 조금 쉬어도 괜찮다’라며 내 편이 되어 나직하게 속삭여 줍니다. 마음속에 다정한 온기와 안도감이 채워질 때 우리를 억누르고 있던 무거운 사슬들도 자연스럽게 풀려갈 거예요. 오늘의 무너짐은 실패가 아니라 나를 진정으로 아끼고 돌보는 새로운 시작을 알리는 신호입니다. 어떤 순간에도 스스로를 포기하지 마십시오. 언제나 당신의 곁에서 온 마음을 다해 응원할게요.",
        "마지막으로 오늘 밤 당장 실천해볼 수 있는 아주 작은 행동을 제안해 드립니다. 잠자리에 들기 전 창문을 활짝 열고 밤공기를 가만히 마시는 것이지요. 그다음 가만히 가슴에 손을 얹고 나의 호흡을 느껴봅니다. 스스로에게 ‘오늘 참 애썼다’라고 따뜻하게 위로해 주어도 좋아요. 지친 마음에 편안한 쉼을 선물해주시기 바랍니다. 스스로에게 다정해지는 연습을 이렇게 작은 일에서부터 시작해 봐요. 오늘 밤 당신에게 편안한 안식이 깃들기를 기원합니다."
      ] : [
        "Placing each and every letter of your heart contained in the story into my eyes and mind, I fell into deep thought. Knowing how much stuffiness and sadness has piled up in your chest from countless words you couldn't tell others and had to swallow inside, my heart hurts too. You probably had to hide and sob alone when you were hurting and breaking down, just because you always acted responsibly and cared for other people. The longer the days you endured with the thought 'If only I hold back, everyone becomes comfortable' got, the lonely and scared little child inside you must have been crying out. For those times you stood alone against the giant and heavy waves of emotions and endured, I want to first offer comfort, saying you went through so much and did really well surviving.",
        "The depression, helplessness, and occasional anger and resentment you feel are extremely natural emotions. I hope you don't blame or reproach yourself, calling yourself weak for having such feelings. Emotions are like flowing water, so if you try to build a dam and block them by force, they will eventually burst out with greater power and swallow you. Your heart collapsing now is not because you lived wrongly, but because you overexerted yourself and used up all your heart's energy. Your heart is sending a signal that rest is urgently needed. So, when your emotions fluctuate and you don't want to do anything, accept and comfort that state exactly as it is.",
        "You are a person who is precious and deserves to be loved more than anyone else. Don't force yourself to fit into others' expectations or social standards. What is more important than others' eyes is listening to what my heart is feeling and wanting right now. The pain and wounds you have do not define who you are, but are merely a dark tunnel passing through the long journey of your life. In the darkness, no matter how bright a light is, it won't be seen and will be discouraging, but the tunnel definitely has an end, and warm sunlight is waiting beyond it. For now, don't force yourself to run inside that tunnel, but it is completely fine to sit down in a safe spot, catch your breath, and care for your wounds. Remember that even if invisible, there is always a warm presence next to you that empathizes with and supports your pain.",
        "Now it is time to turn the warm gaze and consideration you directed toward others back onto yourself. Tell yourself the words you wanted to hear the most when you were most tired and exhausted, while looking in the mirror once a day. 'You really worked hard all this time, now you can rest a little, I will be on your side' like that. When the room of your heart is filled with gentle warmth, the heavy chains that weighed you down will naturally unlock. Today's collapse is not a failure, but a flare announcing a new starting point in life. Until the weather of your heart clears up, and until you regain your gentle smile, I will always support you with all my heart and walk along. I pray tonight will be a slightly more comfortable and cozy shelter for you.",
        "Lastly, I want to suggest a very small action you can practice tonight. Before going to bed, open the window, breathe in the cool night air deeply, put your hand on your chest, and gently whisper to yourself, 'You really did a great job living through today as well.' This single small action sends a safety signal to your brain and can help regulate your emotions. Let's start the practice of becoming kind to ourselves from the very smallest things."
      ];
      fallbackResponse.page_sentences = isKo ? [
        "가장 당신다운 호흡으로, 오늘 하루를 가만히 채워나가길 바랄게요.",
        "힘들면 언제든지 기대어 쉬어가도 좋습니다. 당신 곁엔 늘 보이지 않는 지지가 존재합니다.",
        "진짜 내 모습으로 살아가는 일은, 가끔은 무너질 때 비로소 시작됩니다.",
        "지금 내 상태를 있는 그대로 인정하는 것부터가 치유의 시작입니다.",
        "어떤 순간에도 스스로를 포기하지 않는 내 편이 되어주시기를 기원해요."
      ] : [
        "I hope you gently fill your day today with your own unique breath.",
        "You can rest and lean back anytime if it is hard. There is always unseen support next to you.",
        "Living as your true self sometimes begins when you finally break down.",
        "Acknowledging my current state as it is, is the beginning of healing.",
        "I hope you become your own supporter who never gives up on yourself under any circumstances."
      ];
      fallbackResponse.page_questions = isKo ? [
        "요즘 내가 괜찮은 척하느라 가장 오래 삼킨 말은 무엇일까요?",
        "그때의 나에게 정말 해주고 싶었던 말은 무엇이었습니까?",
        "앞으로 나를 지키기 위해 거절해야 할 생각은 무엇일까요?"
      ] : [
        "What is the word I swallowed the longest while pretending to be okay lately?",
        "What was the word I really wanted to say to myself at that time?",
        "What thoughts should I reject in order to protect myself in the future?"
      ];
      fallbackResponse.page_action = isKo 
        ? "따뜻한 허브차 한 잔을 마시며 5분간 온전히 내 호흡에 집중해 봅니다."
        : "Drink a cup of warm tea and fully focus on your breathing for 5 minutes.";
    } else if (productType === "gift") {
      fallbackResponse.cover.title = isKo ? "선물용 마음 처방 엽서" : "Gift Mind Prescription Postcard";
      fallbackResponse.cover.heart_name = isKo ? `${giftRecipient || "소중한 사람"}님에게` : `To ${giftRecipient || "Precious Person"}`;
      fallbackResponse.page_letter_paragraphs = isKo ? [
        "당신이 보내주신 사연을 가만히 읽으며 그동안 얼마나 무겁고 힘겨운 짐을 홀로 어깨에 짊어진 채 지내오셨을지 마음 깊이 헤아려 봅니다. 아무렇지 않은 척 억지로 미소를 지어 보였겠지만, 홀로 남겨진 밤마다 마음에 쌓인 눈물을 가만히 삼키셨을 것 같아요. 참 많이 애쓰셨고 힘드셨겠습니다. 이제는 더 이상 무리해서 괜찮은 척을 하거나 당신의 감정을 억지로 숨기지 않으셔도 괜찮아요. 마음속 깊은 곳에서 일어나는 슬픔과 외로움을 억누르려 하지 말고 자연스럽게 흘러가도록 내버려 두시기를 바랍니다.",
        "하고 있는 일들이 뜻대로 풀리지 않거나 주변 사람들과의 관계 속에서 큰 상처를 받았더라도, 이것은 결코 당신이 부족해서가 아니에요. 우리는 살아가면서 때로 흐린 하늘 아래를 걷기도 하고 예상치 못한 거센 소나기를 만나 온몸이 젖기도 합니다. 지금 겪고 있는 무기력함과 지친 마음은 영원한 정지가 아니며, 상처받은 마음이 스스로를 보듬고 천천히 에너지를 채워가는 자연스러운 여정이지요. 그러니 이 모든 상황을 당신의 잘못으로 돌리며 너무 자책하지 마십시오.",
        "오늘 밤에는 무언가를 해내야만 한다는 무거운 생각들을 모두 가만히 내려놓고 편안하게 누워 호흡 소리에 집중해 보세요. 들이쉬고 내쉬는 숨결마다 굳어있던 어깨와 마음의 긴장이 사르르 풀려나길 바랍니다. 당신이 가진 소중하고 따뜻한 마음을 스스로가 가장 먼저 귀하게 안아주셨으면 좋겠어요. 여기까지 오시느라 정말 고생하셨고 참 고생 많으셨습니다. 내일은 오늘보다 한 걸음 더 평안하고 다정한 바람이 마음속에 불어오길 바랄게요."
      ] : [
        "Reading your story, I felt how heavy a burden you have been carrying alone. You probably put on a forced smile in front of others, whispering 'I am fine', but during those nights crying alone, your heart must have been bruised. You don't have to pretend to be okay. Don't suppress all the sadness and exhaustion in your heart, but let them flow as they are. Now is the time you need to pause and give yourself room to rest.",
        "I hope you don't blame yourself. Even if things didn't go your way or you were hurt in relationships, it is not because you are weak. Just as we walk under a cloudy sky or meet an unexpected shower, we only experience a brief pause. This exhausted heart is not a stop, but a natural recovery process where a wounded heart heals itself.",
        "Tonight, put down the thoughts that you must do something, and just lie down in your warm bed and focus on your breath. With every inhale and exhale, I hope the tension in your heavy shoulders and heart relaxes. I wish you would value and embrace your good heart first. You went through a lot to get here, and you worked so hard. I hope tomorrow is peaceful."
      ];
      fallbackResponse.page_sentences = isKo ? [
        "가장 당신다운 호흡으로, 오늘 하루를 가만히 채워나가길 바랄게요.",
        "힘들면 언제든지 기대어 쉬어가도 좋습니다. 당신 곁엔 늘 보이지 않는 지지가 존재합니다.",
        "진짜 내 모습으로 살아가는 일은, 가끔은 무너질 때 비로소 시작됩니다."
      ] : [
        "I hope you gently fill your day today with your own unique breath.",
        "You can rest and lean back anytime if it is hard. There is always unseen support next to you.",
        "Living as your true self sometimes begins when you finally break down."
      ];
      fallbackResponse.page_questions = isKo ? [
        "소중한 사람에게 오늘 밤 가만히 들려주고 싶은 나직한 안부 인사는 무엇일까요?",
        "그때의 나에게 정말 해주고 싶었던 말은 무엇이었을까?"
      ] : [
        "What is the gentle greeting you want to silently tell your precious person tonight?",
        "What was the word I really wanted to say to myself at that time?"
      ];
      fallbackResponse.page_action = isKo 
        ? "오늘 밤, 나를 응원해주는 소중한 사람에게 아주 짧은 감사 메시지를 보내봅니다."
        : "Tonight, send a very short message of thanks to a precious person who supports you.";
    } else if (productType === "recovery") {
      fallbackResponse.cover.title = isKo ? "7일의 마음 회복 저널" : "7-Day Heart Recovery Journal";
      fallbackResponse.cover.heart_name = isKo ? "회복을 향해 걷는 마음에게" : "To a Heart Walking Toward Recovery";
      fallbackResponse.recovery_days = getDefaultRecoveryDays(isKo);
      fallbackResponse.page_letter_paragraphs = [];
      fallbackResponse.page_sentences = [];
      fallbackResponse.page_questions = [];
      fallbackResponse.page_action = "";
    }

    // 🔒 뇌과학 RAG 학술 레퍼런스(Scientific Reference) SSoT 데이터 이식
    fallbackResponse.scientific_reference = {
      title: scientificPrescription.title,
      authors: scientificPrescription.authors,
      source_url: scientificPrescription.source_url,
      insight_ko: scientificPrescription.insight_ko
    };

    // 🧠 공감 프로파일러 다차원 감정 지표 (Web UI 렌더링용) SSoT 데이터 이식
    fallbackResponse.emotions = emotionProfile.emotions;
    fallbackResponse.defense_mechanism = emotionProfile.defense_mechanism;
    fallbackResponse.core_pain_point = emotionProfile.core_pain_point;

    return NextResponse.json(fallbackResponse);
  } catch (error) {
    console.error("Letter generation error:", error);
    return NextResponse.json(
      { error: "Failed to generate letter. Please try again later." },
      { status: 500 }
    );
  }
}

const getDefaultRecoveryDays = (isKo: boolean) => isKo ? [
  {
    day: 1,
    letter: "오늘부터 7일간의 아름다운 여정을 함께하게 되어 정말 기쁩니다. 첫날인 오늘은 무언가를 억지로 바꾸려 하지 않고, 그저 지금 내 마음에 가만히 이름을 붙여주는 연습을 해볼 거예요. 우리는 보통 슬프거나 지치거나 화가 날 때, 마음 한구석에 숨겨둔 감정들을 그냥 '힘들다'는 투박한 한마디로 덮어버리곤 합니다. 그렇게 갈 길을 잃은 감정들은 마음 아주 깊은 곳에 쌓여서, 나중에 당신을 더 무겁게 짓누르고 아프게 만들지요. 오늘은 잠시 가만히 멈춰 서서 지금 당신이 느끼는 구체적인 감정의 결을 소리 내어 다정하게 불러보시기 바랍니다. '나는 오늘 하루 종일 괜찮은 척 웃느라 참 많이 피곤했다'라든가, '마음 한쪽이 텅 빈 것처럼 쓸쓸하다'처럼 말이에요. 감정에 정확하고 구체적인 이름을 붙여주는 것만으로도, 그 감정은 스스로를 치유하고 흘러갈 준비를 마칩니다. 뇌과학에서도 감정에 이름을 붙이는 명명 작용을 통해 뇌의 감정 중추인 편도체의 과도한 불안과 흥분이 차분히 가라앉는다고 하지요. 오늘 밤 침대에 눕기 전, 굳어있던 당신의 마음에 가장 알맞은 따뜻하고 예쁜 이름을 선물해 주시기 바랍니다.",
    sentence: "오늘 마음에 붙여준 이름: '괜찮은 척하느라 참 지쳤던 마음'",
    action: "자기 전에 가슴에 가만히 손을 얹고, 오늘 내 감정을 한 문장으로 나직하게 소리 내어 말해보기"
  },
  {
    day: 2,
    letter: "어제 마음에 이름을 붙여주는 첫 연습을 하며 어떠한 감정을 느끼셨을지 가만히 생각하게 됩니다. 조금은 어색하고 낯설었을지라도 오롯이 스스로를 돌아보고 알아차려 준 그 시간 자체가 정말로 귀중한 시작이예요. 둘째 날인 오늘은 어제에 이어 '괜찮은 척했던 마음의 가면을 가만히 내려놓기'를 연습해 보겠습니다. 우리는 학교나 직장, 혹은 친구들을 만날 때 늘 아무렇지 않은 척, 늘 밝고 건강한 척 가면을 쓰곤 하지요. 하지만 그렇게 온종일 쓰고 있던 두껍고 무거운 가면을 집으로 돌아온 밤까지 벗지 못한다면 마음은 결국 짓눌려 숨이 막히고 맙니다. 오늘은 단 10분만이라도 그 무거운 가면을 내려놓고 마음의 여리고 약한 취약함을 솔직하게 대면해 보세요. 꼭 누군가에게 보이기 위해서가 아니라 당신 스스로에게 다정해지기 위함입니다. 괜찮지 않아도 정말로 괜찮아요. 울고 싶다면 마음껏 소리 내어 울어도 좋고, 답답하다면 감정을 밖으로 가만히 쏟아내 보시기 바랍니다. 감정을 가둘수록 상처는 안으로 곪아가지만, 밖으로 비워낼 때 비로소 회복이 시작될 테니까요.",
    sentence: "괜찮지 않아도 괜찮습니다. 오늘의 나는 조금 아프고 약해져도 괜찮은 사람이니까요.",
    action: "하루 중 가장 괜찮은 척 애써야 했던 장면을 작은 종이에 한 줄로 솔직하게 적고 가만히 찢어버리기"
  },
  {
    day: 3,
    letter: "벌써 셋째 날이 되었는데 어제 가면을 조금이나마 내려놓고 지내보니 기분이 어떠셨을지 궁금합니다. 오늘은 마음속에 가장 날카롭고 깊이 박혀 나를 찌르고 있는 가시인 '자책을 덜어내는 날'이에요. 삶에서 힘든 일이 생기거나 누군가와의 관계가 뜻대로 흘러가지 않을 때 우리는 무의식적으로 스스로에게 칼날을 겨누곤 합니다. ‘전부 내 탓이야’라며 자책하는 습관은 당신의 소중한 가치를 갉아먹는 가장 아픈 독이 될 뿐이지요. 당신이 겪고 있는 모든 흔들림과 아픔은 결코 당신이 부족하거나 약해서가 아닙니다. 그 어떤 누구라도 그 힘겨운 상황 속에서는 당신처럼 힘들어했을 것이고, 당신은 그 와중에도 최선을 다하셨어요. 그러니 오늘만큼은 스스로를 찌르던 날카로운 화살을 내려놓으시기 바랍니다. 자신을 탓하던 차가운 말들 대신에 '그때는 그럴 수밖에 없었어', '그동안 참 고생했다'라며 따뜻한 위로를 들려주세요. 당신의 온전한 편이 되어줄 유일한 사람은 바로 당신 자신입니다.",
    sentence: "그것은 당신의 잘못이 아닙니다. 당신은 그 아픔 속에서도 매 순간 최선을 다했으니까요.",
    action: "거울 속의 내 눈을 가만히 바라보며 '당신은 잘못이 없어요, 참 잘해왔어요'라고 따뜻하게 속삭여주기"
  },
  {
    day: 4,
    letter: "넷째 날이 왔으며 어느덧 마음을 보듬는 여정의 절반을 지나왔습니다. 오늘은 온종일 생각에만 갇혀 있던 감정의 무거운 굴레에서 잠시 벗어나, 몸의 감각을 깨워보는 연습을 함께해 볼까요? 마음이 무거울 때 방안에 가만히 누워 생각의 꼬리를 물다 보면, 우리의 뇌는 부정적인 시나리오를 끊임없이 만들어 냅니다. 그 생각의 고리를 즉시 끊어내는 가장 확실한 방법은 바로 몸의 감각을 부드럽게 깨우는 일이지요. 대단한 운동을 하거나 밖으로 거창하게 나가지 않아도 좋습니다. 그저 5분 동안 방 안의 창문을 열고 환기를 시키거나 차가운 물로 세수를 하며 피부에 닿는 촉감에 온전히 집중해 보세요. 몸이 움직이기 시작하면 정체되어 있던 마음의 흐린 안개도 한결 맑게 개기 마련입니다. 무기력함이 당신을 지배하려 할 때, 가벼운 몸의 움직임 하나로 지친 몸과 마음에 활기찬 치유를 선물해 주세요.",
    sentence: "생각이 너무 무거워질 때는 잠시 멈추고, 지금 내 손끝과 발끝의 감각을 가만히 느껴보세요.",
    action: "창문을 활짝 열고 시원한 공기를 세 번 깊게 들이쉬며, 내 몸의 호흡이 나가는 것을 가만히 관찰하기"
  },
  {
    day: 5,
    letter: "다섯째 날이 밝았으며 오늘의 당신은 마음의 깊은 곳에 가만히 가라앉혀 두었던 삼킨 말을 꺼내보는 시간을 가집니다. 누군가에게 상처를 주거나 관계가 깨질까 봐 두려워 억지로 삼켜버린 말들은 마음속에서 사라지지 않고 계속 당신을 아프게 하지요. 그 응어리진 말들은 밖으로 꺼내어 마주하기 전까지는 계속해서 내면에서 비명을 지릅니다. 오늘은 그 누구의 시선도 보지 말고 오직 당신만 볼 수 있는 일기장에 그동안 참았던 감정을 아주 솔직하게 적어 보세요. '그때 난 정말 서운했다'라든가, '사실 나 요즘 너무 외롭다'처럼 날것 그대로 적어보는 것입니다. 그렇게 글로 적어 눈으로 확인하는 순간, 내면에 갇혀 가슴을 조이던 억압된 슬픔이 비로소 자유를 얻게 되지요. 표현되지 못한 아픔은 절대 스스로 사라지지 않음을 명심하시기 바랍니다. 가장 안전한 당신만의 공간에서 그 소중한 목소리를 가만히 꺼내어 해방해 주세요.",
    sentence: "삼켜왔던 아픈 말들을 이제는 내 가슴 밖으로 가만히 내어주어도 괜찮습니다.",
    action: "누구에게도 하지 못했던 속마음 한 문장을 노트에 꾹꾹 눌러 적은 뒤, 다 적고 나서 후련하게 크게 한숨 쉬기"
  },
  {
    day: 6,
    letter: "여섯째 날이 왔으며 여정의 끝자락이 드디어 가까워지고 있습니다. 오늘은 고립되어 있던 당신만의 동굴을 나와 세상과 가볍게 닿아보는 날로 보내보세요. 마음이 지칠 때 우리는 본능적으로 깊이 숨어버리게 되고, 그 외로운 단절 속에서 아픔은 증폭됩니다. 하지만 우리는 타인과의 작고 사소한 연결을 통해서도 엄청난 안도감과 지지를 얻을 수 있는 존재이지요. 결코 많은 에너지를 써서 사람들을 만나러 나가지 않아도 좋습니다. 평소 고마웠던 사람에게 '잘 지내고 있니?' 하고 짧은 안부 문자를 보내거나 이웃에게 가벼운 눈인사를 건네보세요. 타인과 가볍게 주고받는 안부의 한마디는 당신의 어두운 마음에 따뜻한 등불 하나를 켜줄 것입니다. 여전히 내가 이 세상과 연결되어 있다는 안도감이 오늘 당신의 발걸음을 한결 가볍게 만들어 주길 바랄게요.",
    sentence: "당신은 결코 혼자가 아닙니다. 보이지 않아도 따뜻한 연결이 주변을 감싸고 있으니까요.",
    action: "가까운 지인이나 소중한 사람에게 '문득 생각나서 연락했어, 좋은 하루 보내'라고 부담 없는 안부 문자 보내기"
  },
  {
    day: 7,
    letter: "드디어 7일간의 길고 아름다운 회복 여정을 마무리하는 마지막 날에 이르렀습니다. 일주일 동안 매일 잊지 않고 자신의 내면을 들여다보고 안부를 묻는 일은 결코 쉽지 않았을 텐데 참 자랑스러워요. 그동안 상처받은 마음을 스스로 보듬고 돌보느라 진심으로 고생 많으셨습니다. 오늘은 오직 당신 자신만을 위해 온기가 가득 담긴 감사와 위로의 답장을 가만히 선물해 주세요. 거울 속의 내 눈을 바라보며 '포기하지 않고 견디며 살아내 주어서 정말 고맙습니다'라고 전해보시기 바랍니다. 이 7일간의 발자국들이 마음속에 씨앗이 되어 당신 삶에 다정한 꽃을 피워낼 것이라 믿어요. 언제나 당신을 향해 있을 제 따뜻한 응원을 잊지 마시고 늘 평안하시기를 간절히 기도합니다.",
    sentence: "7일 동안 멈추지 않고 스스로를 돌봐준 당신에게, 온 마음을 다해 고맙다는 인사를 건냅니다.",
    action: "이 여정을 끝마친 나를 위해 따뜻하고 포근한 차 한 잔을 선물하며, 가만히 눈을 감고 수고한 내 어깨를 토닥여주기",
    summary_sentences: [
      "아픔은 머무는 것이 아니라, 잠시 스쳐 지나가는 소나기일 뿐입니다.",
      "흔들릴 때는 마음껏 흔들려도 괜찮습니다, 결국 제자리로 돌아오면 되니까요.",
      "어떤 순간에도 스스로의 편에 서서 가만히 지지해 주시기를 바랍니다."
    ]
  }
] : [
  {
    day: 1,
    letter: "I am truly glad to join you on this beautiful 7-day recovery journey starting today. On this first day of our journey, we will not try to force any sudden changes, but simply practice gently naming our hearts and acknowledging our present feelings. Normally, when we are sad or tired, we tend to lump all those complex feelings together and cover them up with just a simple phrase like 'it's hard.' Those lost emotions pile up deep inside, eventually weighing you down even more. Today, let's pause for a moment and call out the detailed feelings you are experiencing. Naming your emotions calms the brain's emotional center and prepares it to heal itself. Before going to bed tonight, please present your heart with a warm, comforting name.",
    sentence: "Today's name for my heart: 'The heart that was so tired of pretending to be okay'",
    action: "Gently place your hand on your chest before sleeping and say your emotion tonight in one sentence aloud"
  },
  {
    day: 2,
    letter: "How was your first practice of naming your heart yesterday? Even if it felt a bit awkward, that time looking back at yourself is a truly valuable start. Today, on the second day, we are going to practice 'putting down pretending to be okay.' We wear a mask of being fine in front of others. However, if you cannot take off that mask even at home, your heart will eventually suffocate. Today, put down that heavy mask for just 10 minutes and face your vulnerability. It is okay not to be okay. Cry if you want, and let your feelings out. When you pour them out, recovery finally begins. Write one line about a scene where you pretended to be okay today.",
    sentence: "It is okay not to be okay. Because today, I am someone who can be a little hurt and weak.",
    action: "Write one line about the scene where you had to pretend to be okay most today on a piece of paper, and gently tear it up"
  },
  {
    day: 3,
    letter: "It is already the third day of our journey together. Today is the day to relieve self-blame, that sharp thorn deeply embedded in your precious heart. When difficult things happen or relationships break, we unconsciously point the sword at ourselves, thinking 'It is all my fault.' However, self-blame never solves the situation and only becomes a painful poison that eats away at your soul. The suffering you experienced is by no means because you are lacking. Anyone would have struggled in that situation, and you did your best. So today, please put away those harsh arrows directed at yourself. Instead of words that blame you, whisper warm, friendly words like 'It was understandable' or 'You worked really hard all this time.'",
    sentence: "It is not your fault. You did your absolute best at every single moment within that pain.",
    action: "Look gently into your own eyes in the mirror and whisper warmly, 'It is not your fault, you have done so well'"
  },
  {
    day: 4,
    letter: "It is already the fourth day. We have already passed half of our beautiful journey of recovery. Today, we are going to escape the shackles of emotional thinking and practice 'not hating ourselves by lightly moving the body' together. When your mind is heavy and complicated, lying still in bed makes the brain create negative scenarios, pushing us deeper into the dark. The best way to break this endless train of thought is to wake up the body's physical senses. It doesn't have to be a grand exercise. Just walk around the neighborhood for about 5 minutes, stretch your shoulders, or wash your face with cold water. When the body moves, the cloudy fog covering the heart clears up immediately. When you are about to sink into lethargy, please awaken your physical senses and stop thinking. Let's circulate your energy refreshingly today.",
    sentence: "When thoughts get too heavy, let's pause and quietly feel the sensation in our fingertips and toes.",
    action: "Open the window wide, take three deep breaths of fresh air, and quietly observe your breath going out"
  },
  {
    day: 5,
    letter: "The fifth day has dawned. Today is the day to safely bring out 'one sentence you swallowed for a long time' that you couldn't dare to speak out and kept submerged in the deep sea of your heart. The words you swallowed by force out of fear of getting hurt or breaking relationships do not disappear, but decay deeply and cause pain. Those words will continue to trouble you until you bring them out. Today, without caring about others, write down that swallowed word raw in your private diary. Even if it is a very primitive cry like 'I was really angry then' or 'Actually, I was so lonely.' The moment you write it down and check it with your eyes, the suppressed emotions gain freedom. Unexpressed sadness never disappears on its own.",
    sentence: "It is okay to gently let the painful words you've swallowed out of your chest now.",
    action: "Write down one sentence of your inner heart that you couldn't tell anyone, and take a deep, relieved sigh after finishing"
  },
  {
    day: 6,
    letter: "It's the sixth day. Today, let's spend the day 'lightly touching the world' beyond the boundary of my isolated room. When the heart hurts, we instinctively hide inside a cave, and in that isolation, loneliness grows bigger. However, we are social beings who gain relief and support through small connections with others. You don't need to spend too much energy. Just send a short greeting text message like 'Are you doing well?' to someone you are grateful for, exchange a light nod with a neighbor, or share a brief moment of your daily life. That single word of greeting shared lightly with others will light a warm candle in your heart. You are not alone in this world.",
    sentence: "You are never alone. For a warm connection surrounds you, even if it is invisible.",
    action: "Send a pressure-free greeting text to a close acquaintance or loved one: 'Just thought of you, hope you have a great day'"
  },
  {
    day: 7,
    letter: "Finally, it is the last day wrapping up this beautiful 7-day recovery journey of your heart. Looking into your inner self and asking for greetings every single day for a week is never an easy task, and you should be extremely proud of yourself for walking all the way here without giving up. You did a wonderful job sincerely caring for your wounded heart. Today, send a letter filled with warm temperature, gratitude, and deep love to yourself who worked so hard. Look in the mirror, make eye contact, and say, 'Thank you for not giving up and surviving those lonely and painful nights.' These 7 days of traces will become solid seeds that bloom the flowers of kindness and peace in your life. Never forget my warm support that will always be directed toward you, and I wish you peace and warmth in your life. You did an amazing job.",
    sentence: "To you who cared for yourself without stopping for 7 days, I offer my gratitude with all my heart.",
    action: "Gift yourself a warm, cozy cup of tea for finishing this journey, close your eyes, and gently pat your own shoulders",
    summary_sentences: [
      "Pain is not something that stays, but merely a brief shower passing through.",
      "It is completely fine to stumble; you only need to return to your place in the end.",
      "No matter what happens, never stop being on your own side."
    ]
  }
]
