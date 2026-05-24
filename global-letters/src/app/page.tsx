"use client";

import { useState, useRef, useEffect } from "react";
import { PayPalButtons } from "@paypal/react-paypal-js";

type ProductType = "random" | "free" | "beta" | "deep" | "recovery" | "gift";
type ViewState = "input" | "tier" | "payment" | "loading" | "full";

interface LetterData {
  cover: { title: string; heart_name: string };
  page_letter_paragraphs: string[];
  page_sentences: string[];
  page_questions: string[];
  page_action: string;
  recovery_days?: { day: number; letter: string; action: string }[];
  letter?: string;
  action?: string;
}

const TIERS = [
  { id: "random", name: "Random", desc: "Daily sentence pick", priceText: "Free", priceVal: 0, usd: "0" },
  { id: "free", name: "Free", desc: "Short supportive letter based on your story", priceText: "Free (once per day)", priceVal: 0, usd: "0" },
  { id: "beta", name: "Beta", desc: "Standard prescription and psychological analysis", priceText: "$3.99", priceVal: 5000, usd: "3.99" },
  { id: "deep", name: "Deep", desc: "Deep psychological analysis and action guidance", priceText: "$6.99", priceVal: 9000, usd: "6.99" },
  { id: "recovery", name: "Recovery", desc: "7-day focused recovery journey", priceText: "$21.99", priceVal: 29000, usd: "21.99" },
  { id: "gift", name: "Gift Package", desc: "Gift a comforting PDF postcard to someone special", priceText: "$9.99", priceVal: 12000, usd: "9.99", popular: true }
];

const aestheticBackgrounds = [
  "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1436891620584-47fd0e565afb?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1470770903672-71aa615dd6f4?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1518173946687-a4c8892bbd9f?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1445905595283-21f8ae8a33d2?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1532274402911-5a369e4c48f2?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1483728642387-6c3ba6c6af81?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1422405153578-4bd676b19036?q=80&w=1000&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=1000&auto=format&fit=crop"
];

const translations = {
  ko: {
    appTitle: "마음을 묻다",
    appSubtitle: "당신의 짐을 잠시 내려놓으세요. 따뜻한 편지로 답해드립니다.",
    selectTier: "어떤 처방을 원하시나요?",
    goBack: "뒤로 가기",
    chooseTier: "처방전 선택하기",
    inputHelpRegular: "짧아도 괜찮습니다. 다만 500자 안팎으로 적어주시면 당신의 마음에 더 잘 맞는 문장으로 써드릴 수 있습니다.",
    inputHelpRecovery: "7일 동안 함께 다독일 마음이라, 조금 자세히 적어주시면 좋습니다. 반복해서 무너지는 순간, 7일 뒤 바라는 마음까지 편하게 적어주세요.",
    q1Name: "1. 어떤 이름으로 불러드릴까요?",
    q2Category: "2. 지금 가장 가까운 마음을 골라주세요.",
    q2CategoryPlaceholder: "선택해주세요",
    q2CategoryOptions: [
      "너무 오래 버틴 마음",
      "괜찮은 척하느라 지친 마음",
      "혼자 울고 있는 마음",
      "사람에게 상처받은 마음",
      "다시 사랑받고 싶은 마음"
    ],
    q3Swallowed: "3. 요즘 가장 자주 삼키는 말은 무엇인가요?",
    q4Wants: "4. 지금 가장 듣고 싶은 말은 무엇인가요?",
    q5Avoid: "5. 원하지 않는 표현이나 피하고 싶은 말이 있나요?",
    q6Comfort: "6. 당신을 가장 편안하게 만드는 한 가지는 무엇인가요?",
    q7Wish: "7. 이 편지에 꼭 담겼으면 하는 한 문장을 적어주세요.",
    recoveryQ2Core: "2. 7일 동안 가장 다독이고 싶은 마음은 무엇인가요?",
    recoveryQ3Breakdown: "3. 요즘 반복해서 무너지는 순간은 언제인가요?",
    recoveryQ4Wish: "4. 7일 뒤 어떤 마음이 되었으면 하나요?",
    recoveryQ5Time: "5. 하루 중 가장 마음이 무너지는 시간대는 언제인가요?",
    recoveryQ6Action: "6. 그래도 해볼 수 있을 것 같은 아주 작은 행동이 있다면?",
    recoveryQ7Support: "7. 회복을 위해 지금 가장 필요한 한 가지는 무엇인가요?",
    questionsCompleted: "질문 입력 완료",
    nextStep: "다음 단계로",
    tierNames: {
      random: "Random",
      free: "Free",
      beta: "Beta",
      deep: "Deep",
      recovery: "Recovery",
      gift: "Gift Package"
    },
    tierDescriptions: {
      random: "오늘의 문장 (랜덤 뽑기)",
      free: "사연 기반 짧은 안부 편지",
      beta: "표준 처방전 및 심리 분석",
      deep: "심층 심리 분석 및 행동 지침",
      recovery: "7일 집중 회복 여정 (연속 처방)",
      gift: "소중한 사람에게 위로를 선물하세요 (PDF 엽서 발급)"
    },
    tierPriceText: {
      random: "무료",
      free: "무료 (일 1회)",
      beta: "5,000원 ($3.99)",
      deep: "9,000원 ($6.99)",
      recovery: "29,000원 ($21.99)",
      gift: "12,000원 ($9.99)"
    },
    popular: "인기",
    paymentSuffix: "처방전 결제",
    paymentDesc: "결제를 완료하시면 마스터 오영범의 따뜻한 편지가 즉시 작성됩니다.",
    giftRecipientLabel: "선물 받을 분의 성함(또는 애칭)을 적어주세요.",
    giftRecipientPlaceholder: "예: 사랑하는 지우님",
    giftRecipientEmailLabel: "선물 받을 분의 이메일 주소를 적어주세요.",
    giftRecipientEmailPlaceholder: "예: email@example.com",
    testPaymentBypass: "✨ [테스트용] 결제 우회 (개발자 전용)",
    loadingText: "당신의 이야기를 깊이 들여다보고 있습니다...",
    randomLoadingText: "오늘의 문장을 뽑고 있습니다...",
    pdfLoadingText: "💌 PDF 저장 중...",
    pdfDownloadLabel: "나만의 엽서 간직하기 (PDF)",
    pdfPermanentLabel: "이 처방전 영구 소장하기 (PDF 다운로드)",
    keepForever: "이 처방전 영구 소장하기 (PDF 다운로드)",
    storyHeader: "마음을 묻다",
    freeCardLabel: "마음을 묻다",
    premiumSentenceHeader: "오래 간직할 문장",
    premiumQuestionHeader: "나에게 묻는 질문",
    premiumActionHeader: "오늘의 작은 행동",
    recoveryDayHeader: "일차 회복 편지",
    reviewTitle: "오늘의 편지가 위로가 되었나요?",
    reviewSubtitle: "소중한 피드백을 남겨주시면 대표님께 전달됩니다. ✨",
    reviewPlaceholder: "당신의 마음에 어떤 변화가 있었나요? 감상평을 편하게 남겨주세요...",
    reviewSubmit: "리뷰 전송하기",
    reviewSuccess: "리뷰가 성공적으로 전송되었습니다. 소중한 피드백 감사합니다! 💛",
    reset: "처음으로 돌아가기",
    footerBrand: "마음을 묻다",
    footerCopyright: "© 2026 Master O.Y.B ALL RIGHTS RESERVED.",
    alertSelectTier: "먼저 원하는 처방전을 선택해주세요.",
    alertFillMore: "질문을 조금 더 작성해 주세요. 진짜 당신의 마음을 담아주세요.",
    alertDrawLimit: "오늘의 문장 뽑기는 하루에 3번까지만 가능합니다. 내일 다시 새로운 문장을 만나보세요! ✨",
    alertLetterError: "편지 생성 중 오류가 발생했습니다.",
    alertPdfError: "PDF 생성 중 오류가 발생했습니다.",
    pdfErrorDetail: "PDF 생성 중 오류가 발생했습니다.\n\n오류 내용: ",
    payPalError: "PDF 인쇄 라이브러리(Pro) 로드 실패: ",
    pdfLibError: "PDF 구성 파일(jsPDF)이 아직 로드되지 않았습니다.",
    pdfFilename: "마음을_묻다_위로엽서.pdf"
  },
  en: {
    appTitle: "Ask Your Heart",
    appSubtitle: "Leave your worries behind for a moment. We'll answer with a warm letter.",
    selectTier: "Which prescription do you need?",
    goBack: "Go Back",
    chooseTier: "Select prescription",
    inputHelpRegular: "A short note is fine. About 500 characters helps us write a more fitting letter for your feelings.",
    inputHelpRecovery: "This is a 7-day recovery journey, so please describe your feelings in detail. Include repeated breakdown moments and what you hope to feel after 7 days.",
    q1Name: "1. What name should we call you?",
    q2Category: "2. Choose the feeling closest to you right now.",
    q2CategoryPlaceholder: "Please choose",
    q2CategoryOptions: [
      "A heart that has endured too long",
      "A heart tired of pretending to be okay",
      "A heart crying alone",
      "A heart hurt by others",
      "A heart wanting to be loved again"
    ],
    q3Swallowed: "3. What phrase do you find yourself swallowing most often these days?",
    q4Wants: "4. What words do you most want to hear right now?",
    q5Avoid: "5. Is there any phrase you don't want to hear or want to avoid?",
    q6Comfort: "6. What is one thing that makes you feel most comfortable?",
    q7Wish: "7. Write one sentence you want included in this letter.",
    recoveryQ2Core: "2. What heart do you want to comfort most during these 7 days?",
    recoveryQ3Breakdown: "3. When do you find yourself breaking down repeatedly these days?",
    recoveryQ4Wish: "4. What kind of heart do you want to have after 7 days?",
    recoveryQ5Time: "5. When during the day does your heart feel the weakest?",
    recoveryQ6Action: "6. What's one small action you think you can still try?",
    recoveryQ7Support: "7. What do you need most right now for recovery?",
    questionsCompleted: "questions filled",
    nextStep: "Continue",
    tierNames: {
      random: "Random",
      free: "Free",
      beta: "Beta",
      deep: "Deep",
      recovery: "Recovery",
      gift: "Gift Package"
    },
    tierDescriptions: {
      random: "Daily sentence pick",
      free: "Short supportive letter based on your story",
      beta: "Standard prescription and psychological analysis",
      deep: "Deep psychological analysis and action guidance",
      recovery: "7-day focused recovery journey",
      gift: "Gift comfort to someone special with a PDF postcard"
    },
    tierPriceText: {
      random: "Free",
      free: "Free (once per day)",
      beta: "$3.99",
      deep: "$6.99",
      recovery: "$21.99",
      gift: "$9.99"
    },
    popular: "Popular",
    paymentSuffix: "prescription payment",
    paymentDesc: "After payment, a warm letter from Master O.Y.B will be created immediately.",
    giftRecipientLabel: "Enter the recipient's name or nickname.",
    giftRecipientPlaceholder: "e.g. Jiwon, my dear",
    giftRecipientEmailLabel: "Enter the recipient's email address.",
    giftRecipientEmailPlaceholder: "e.g. email@example.com",
    testPaymentBypass: "✨ [Test only] Payment bypass (dev only)",
    loadingText: "We are looking deeply into your story...",
    randomLoadingText: "Picking today's sentence...",
    pdfLoadingText: "💌 Saving PDF...",
    pdfDownloadLabel: "Save my postcard (PDF)",
    pdfPermanentLabel: "Keep this prescription forever (PDF download)",
    keepForever: "Keep this prescription forever (PDF download)",
    storyHeader: "Ask Your Heart",
    freeCardLabel: "Ask Your Heart",
    premiumSentenceHeader: "Sentences to cherish",
    premiumQuestionHeader: "Questions for yourself",
    premiumActionHeader: "Today's small action",
    recoveryDayHeader: "Day recovery letter",
    reviewTitle: "Did today's letter comfort you?",
    reviewSubtitle: "Your feedback will be delivered to the team. ✨",
    reviewPlaceholder: "How did this letter change your feelings? Share your thoughts.",
    reviewSubmit: "Send review",
    reviewSuccess: "Your review has been submitted successfully. Thank you for your precious feedback! 💛",
    reset: "Start over",
    footerBrand: "Ask Your Heart",
    footerCopyright: "© 2026 Master O.Y.B ALL RIGHTS RESERVED.",
    alertSelectTier: "Please select a prescription first.",
    alertFillMore: "Please write a bit more. Put your true feelings into the questions.",
    alertDrawLimit: "Daily sentence draw is limited to 3 times per day. Please return tomorrow for a new sentence! ✨",
    alertLetterError: "An error occurred while creating the letter.",
    alertPdfError: "An error occurred while generating the PDF.",
    pdfErrorDetail: "An error occurred while generating the PDF.\n\nError: ",
    payPalError: "Failed to load PDF print library (Pro): ",
    pdfLibError: "PDF library (jsPDF) is not loaded yet.",
    pdfFilename: "ask-your-heart-letter.pdf"
  }
};

const paginateParagraphs = (paragraphs: string[], maxPageHeightPx: number = 720) => {
  if (typeof window === "undefined") return [paragraphs];
  const pages: string[][] = [[]];
  let currentPageIndex = 0;
  
  // Create a temporary hidden container to measure paragraph heights
  const tempContainer = document.createElement("div");
  tempContainer.style.width = "210mm";
  tempContainer.style.padding = "20mm";
  tempContainer.style.boxSizing = "border-box";
  tempContainer.style.fontFamily = "'Apple SD Gothic Neo', 'Malgun Gothic', 'Playfair Display', serif";
  tempContainer.style.fontSize = "1.125rem"; // text-lg equivalent
  tempContainer.style.lineHeight = "2.25"; // leading-loose equivalent
  tempContainer.style.position = "fixed";
  tempContainer.style.top = "-9999px";
  tempContainer.style.left = "-9999px";
  document.body.appendChild(tempContainer);

  for (const para of paragraphs) {
    // Append the paragraph to the current temp container to test size
    const pElement = document.createElement("p");
    pElement.style.marginBottom = "1.5rem"; // mb-6 equivalent
    pElement.innerText = para;
    tempContainer.appendChild(pElement);

    // Measure height
    if (tempContainer.scrollHeight > maxPageHeightPx && pages[currentPageIndex].length > 0) {
      // If it overflows the max height, move this paragraph to a new page
      currentPageIndex += 1;
      pages[currentPageIndex] = [para];
      
      // Reset the temp container and put only the new paragraph in it
      tempContainer.innerHTML = "";
      const newPElement = document.createElement("p");
      newPElement.style.marginBottom = "1.5rem";
      newPElement.innerText = para;
      tempContainer.appendChild(newPElement);
    } else {
      // Otherwise, add it to the current page list
      pages[currentPageIndex].push(para);
    }
  }

  // Clean up
  document.body.removeChild(tempContainer);
  return pages;
};

export default function Home() {
  const [view, setView] = useState<ViewState>("tier");
  const [envelopeOpen, setEnvelopeOpen] = useState(false);
  const [userStory, setUserStory] = useState("");
  const [productType, setProductType] = useState<ProductType>("free");
  const [typedText, setTypedText] = useState("");
  const [fullLetterText, setFullLetterText] = useState("");
  const [actionStep, setActionStep] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showAction, setShowAction] = useState(false);
  const [letterData, setLetterData] = useState<LetterData | null>(null);
  const [drawCount, setDrawCount] = useState(0);
  const [bgUrl, setBgUrl] = useState("");
  const [mounted, setMounted] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<typeof TIERS[0] | null>(null);
  const [giftRecipient, setGiftRecipient] = useState("");
  const [giftRecipientEmail, setGiftRecipientEmail] = useState("");
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isKorean, setIsKorean] = useState(true);
  const t = isKorean ? translations.ko : translations.en;

  // 통계 및 리뷰용 상태 추가
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  // 🔒 타이핑 락 및 클로저 상태 수호용 Ref 객체
  const fullLetterRef = useRef("");
  const actionStepRef = useRef("");
  const isTypingRef = useRef(false);

  const getPaginatedParagraphs = () => {
    if (!letterData) return [[]];
    const paras = letterData.page_letter_paragraphs?.length 
      ? letterData.page_letter_paragraphs 
      : [letterData.letter || ""];
    
    return paginateParagraphs(paras, 750);
  };

  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined" && navigator.language) {
      setIsKorean(navigator.language.toLowerCase().includes('ko'));
    }
    
    // 엽서 배경을 15종 엄선 리스트에서 임의 선택하여 초기화
    const randomBg = aestheticBackgrounds[Math.floor(Math.random() * aestheticBackgrounds.length)];
    setBgUrl(randomBg);

    const today = new Date().toDateString();
    try {
      const saved = localStorage.getItem("sentence_draw_data");
      if (saved) {
        const { date, count } = JSON.parse(saved);
        if (date === today) {
          setDrawCount(count);
        } else {
          localStorage.setItem("sentence_draw_data", JSON.stringify({ date: today, count: 0 }));
        }
      } else {
        localStorage.setItem("sentence_draw_data", JSON.stringify({ date: today, count: 0 }));
      }
    } catch (e) {
      localStorage.setItem("sentence_draw_data", JSON.stringify({ date: today, count: 0 }));
    }

    // [추가] 방문자 트래픽 추적 백엔드 전송 (Next.js serverless relative route)
    fetch("/api/track/visit", { method: "POST" })
      .catch((err) => console.log("Traffic tracking dev mode"));
  }, []);

  const typingRef = useRef<NodeJS.Timeout | null>(null);



  const makeLegacyLetter = (data: any) => {
    if (!data) return "";
    if (typeof data.letter === "string" && data.letter.trim() !== "") {
      return data.letter;
    }
    const paragraphs = Array.isArray(data.page_letter_paragraphs)
      ? data.page_letter_paragraphs
      : [];
    const sentences = Array.isArray(data.page_sentences)
      ? data.page_sentences.map((s: string) => `"${s}"`)
      : [];
    const questions = Array.isArray(data.page_questions)
      ? data.page_questions.map((q: string) => `Q. ${q}`)
      : [];

    return [...paragraphs, sentences.join("\n"), questions.join("\n")]
      .filter(Boolean)
      .join("\n\n");
  };

  const handleFormChange = (questionId: string, value: string) => {
    setFormData((prev) => ({ ...prev, [questionId]: value }));
  };

  const buildStoryPayload = () => {
    const filledKeys = Object.keys(formData);
    let payload = userStory.trim() ? `사연: ${userStory.trim()}\n\n` : "";
    if (filledKeys.length > 0) {
      payload += filledKeys
        .map((key) => `${key}: ${formData[key].trim()}`)
        .filter(Boolean)
        .join("\n\n");
    }
    return payload || userStory.trim();
  };

  const handleFormSubmit = () => {
    if (!selectedProduct) {
      alert(t.alertSelectTier);
      setView("tier");
      return;
    }

    const filledCount = Object.values(formData).filter((value) => value.trim().length > 0).length;
    if (filledCount < 4) {
      alert(t.alertFillMore);
      return;
    }

    if (selectedProduct.priceVal > 0) {
      setView("payment");
      return;
    }

    generateLetter(selectedProduct.id as ProductType);
  };

  const handleSelectTier = (tier: typeof TIERS[0]) => {
    setSelectedProduct(tier);
    setProductType(tier.id as ProductType);
    setFormData({});

    if (tier.id === "random") {
      handleDrawGreeting();
      return;
    }

    setView("input");
  };

  const handleDrawGreeting = async () => {
    if (drawCount >= 3) {
      alert(t.alertDrawLimit);
      return;
    }
    const today = new Date().toDateString();
    const newCount = drawCount + 1;
    setDrawCount(newCount);
    localStorage.setItem("sentence_draw_data", JSON.stringify({ date: today, count: newCount }));
    await generateLetter("random");
  };

  const generateLetter = async (type: ProductType) => {
    setView("loading");
    try {
      // 엽서 배경을 15종 엄선 리스트에서 임의 선택하여 로드 (Unsplash API 에러 완전 방지)
      const randomBg = aestheticBackgrounds[Math.floor(Math.random() * aestheticBackgrounds.length)];
      setBgUrl(randomBg);

      const response = await fetch("/api/generate-letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ story: buildStoryPayload(), productType: type, giftRecipient, language: isKorean ? "ko" : "en" }),
      });
      const data = await response.json();
      if (data.error) {
        alert(data.error);
        setView("tier");
        return;
      }
      setLetterData(data);
      
      const legacyText = makeLegacyLetter(data);
      let letterBody = data.letter || legacyText;
      
      // Random 모드일 경우 AI가 자체 생성한 따옴표 제거 (UI에 이미 고정 따옴표가 있으므로 중복 방지)
      if (type === "random") {
        letterBody = letterBody.trim().replace(/^["'“”‘’]+|["'“”‘’]+$/g, '').trim();
      }
      
      fullLetterRef.current = letterBody;
      actionStepRef.current = data.action || data.page_action || "";
      
      setFullLetterText(letterBody);
      setView("full");
      startTyping(letterBody, data.action || data.page_action || "");

      // 🎁 선물 패키지 요금제 결제 시 수신자에게 이메일 자동 발송 트리거 실행
      if (type === "gift" && giftRecipient && giftRecipientEmail) {
        fetch("/api/send-gift", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            recipientName: giftRecipient,
            recipientEmail: giftRecipientEmail,
            senderName: formData.q1_name || (isKorean ? "소중한 사람" : "Someone special"),
            letterData: data
          })
        })
        .then(res => res.json())
        .then(emailRes => {
          if (emailRes.success) {
            console.log("💌 [선물 편지 발송] 이메일 발송 결과:", emailRes.mode);
          } else {
            console.error("❌ [선물 편지 발송] 발송 오류:", emailRes.error);
          }
        })
        .catch(err => {
          console.error("❌ [선물 편지 발송] API 연동 실패:", err);
        });
      }

    } catch (error) {
      alert(t.alertLetterError);
      setView("tier");
    }
  };

  const startTyping = (text: string, action: string) => {
    fullLetterRef.current = text;
    actionStepRef.current = action;
    isTypingRef.current = true;

    setActionStep(action);
    setTypedText("");
    setIsTyping(true);
    setShowAction(false);
    let i = 0;
    const typeNextChar = () => {
      // 🔒 skipTyping으로 취소 상태가 되었다면 타이머 루프 즉시 탈출
      if (!isTypingRef.current) return;
      
      if (i < text.length) {
        setTypedText(text.substring(0, i + 1));
        i++;
        typingRef.current = setTimeout(typeNextChar, 30);
      } else {
        finishTyping();
      }
    };
    typingRef.current = setTimeout(typeNextChar, 30);
  };

  const finishTyping = () => {
    isTypingRef.current = false;
    if (typingRef.current) clearTimeout(typingRef.current);
    setIsTyping(false);
    setTypedText(fullLetterRef.current);
    setShowAction(true);
  };

  const skipTyping = () => {
    if (isTypingRef.current) {
      finishTyping();
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      rating,
      content: reviewText,
      tier: productType
    };
    try {
      await fetch("/api/track/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setReviewSubmitted(true);
    } catch (err) {
      console.log("Review tracking dev mode error:", err);
      setReviewSubmitted(true); // 오프라인/개발 환경에서도 성공 메시지 노출
    }
  };

  const resetForm = () => {
    setUserStory("");
    setReviewText("");
    setRating(5);
    setReviewSubmitted(false);
    setView("tier");
    setSelectedProduct(null);
    setEnvelopeOpen(false);
    setGiftRecipient("");
    setGiftRecipientEmail("");
    setFormData({});
    
    // 🔒 상태값 및 Ref 초기화 추가
    setTypedText("");
    setFullLetterText("");
    setIsTyping(false);
    setShowAction(false);
    fullLetterRef.current = "";
    actionStepRef.current = "";
    isTypingRef.current = false;
    if (typingRef.current) clearTimeout(typingRef.current);
    
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDownloadPDF = async () => {
    const hiddenPages = Array.from(document.querySelectorAll('.pdf-page')) as HTMLElement[];
    const pageElements = hiddenPages.length > 0
      ? hiddenPages
      : [document.getElementById("letter-container")].filter(Boolean) as HTMLElement[];
    if (pageElements.length === 0) return;

    const downloadBtn = document.querySelector("#download-pdf-btn");
    const originalText = downloadBtn?.innerHTML;

    if (downloadBtn) {
      downloadBtn.innerHTML = t.pdfLoadingText;
      (downloadBtn as any).disabled = true;
    }

    const forceLoadProEngine = (): Promise<any> => {
      return new Promise((resolve, reject) => {
        if ((window as any).html2canvasProInstance) {
          resolve((window as any).html2canvasProInstance);
          return;
        }

        const script = document.createElement("script");
        script.src = "https://cdn.jsdelivr.net/npm/html2canvas-pro@latest/dist/html2canvas-pro.min.js";
        script.crossOrigin = "anonymous";
        script.onload = () => {
          (window as any).html2canvasProInstance = (window as any).html2canvas;
          resolve((window as any).html2canvas);
        };
        script.onerror = (e) => reject(new Error(t.payPalError + e));
        document.head.appendChild(script); // Fix: Actually append the script to start loading
      });
    };

    try {
      const proEngine = await forceLoadProEngine();
      const jsPDF = (window as any).jsPDF || ((window as any).jspdf ? (window as any).jspdf.jsPDF : null);
      if (!jsPDF) {
        throw new Error(t.pdfLibError);
      }

      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();

      for (let pageIndex = 0; pageIndex < pageElements.length; pageIndex += 1) {
        const pageElement = pageElements[pageIndex];
        const canvas = await proEngine(pageElement, {
          scale: 3,
          useCORS: true,
          logging: false,
          backgroundColor: "#ffffff",
          allowTaint: false,
        });

        const imgData = canvas.toDataURL('image/jpeg', 1.0);
        const imgWidth = pdfWidth - 20;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        const yPos = (pdfHeight - imgHeight) / 2;

        if (pageIndex > 0) pdf.addPage();
        pdf.addImage(imgData, 'JPEG', 10, yPos > 10 ? yPos : 10, imgWidth, imgHeight);
      }

      pdf.save('마음을_묻다_위로엽서.pdf');
    } catch (err: any) {
      console.error("PDF generation error:", err);
      alert(t.pdfErrorDetail + (err?.message || err));
    } finally {
      if (downloadBtn) {
        downloadBtn.innerHTML = originalText || t.pdfDownloadLabel;
        (downloadBtn as any).disabled = false;
      }
    }
  };

  return (
    <div className={`min-h-screen flex flex-col items-center relative selection:bg-amber-100 overflow-x-hidden font-serif transition-all duration-1000 ${
      view === "full" ? "desk-bg text-slate-100" : "bg-[#fdfbf7] text-slate-800"
    }`}>
      {/* Floating Glassmorphic KO | EN Language Toggle */}
      <div className="absolute top-6 right-6 z-50">
        <button
          onClick={() => setIsKorean(prev => !prev)}
          className="backdrop-blur-xl border border-slate-200/50 bg-white/40 text-slate-700 rounded-full py-1.5 px-4 text-xs font-sans font-medium hover:bg-white/60 active:scale-95 transition-all shadow-[0_4px_30px_rgba(0,0,0,0.03)] cursor-pointer flex items-center gap-1.5 hover:border-slate-300/50"
        >
          <svg className="w-3.5 h-3.5 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5c-.347 2.117-1.127 4.195-2.28 6.095M6.412 9a9.616 9.616 0 013.28-3m-3.28 3h8.218" />
          </svg>
          {isKorean ? "KO | EN" : "EN | KO"}
        </button>
      </div>

        <div className="w-full max-w-4xl px-4 sm:px-6 py-12 md:py-16 flex flex-col items-center">
          
          {/* Header (Hidden on result view) */}
          {view !== "full" && (
            <header className="text-center mb-10 w-full max-w-3xl animate-fade-in transition-opacity duration-700">
              <h1 className="font-serif text-4xl md:text-5xl font-bold text-slate-800 mb-4 tracking-tight leading-tight">
                {t.appTitle}
              </h1>
              <p className="text-slate-500 text-lg font-serif">
                {t.appSubtitle}
              </p>
            </header>
          )}

          <main className="w-full max-w-4xl relative flex flex-col items-center">
            
            {/* 1. 사연 입력창 */}
            {view === "input" && (
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-8 md:p-12 w-full max-w-4xl border border-white shadow-layered transition-all duration-500 animate-fade-in">
                <div className="w-full mt-4 flex flex-col gap-6 animate-fade-in text-left">
                  {!selectedProduct ? (
                    <div className="rounded-3xl border border-amber-100 bg-amber-50/80 p-8 text-center text-slate-700 font-serif">
                      {t.alertSelectTier}
                      <button
                        type="button"
                        onClick={() => setView("tier")}
                        className="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-800 transition"
                      >
                        {t.chooseTier}
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="p-4 bg-slate-50 rounded-3xl text-sm text-slate-500 font-serif">
                        {selectedProduct.id === "recovery" ? t.inputHelpRecovery : t.inputHelpRegular}
                      </div>

                      <div>
                        <label className="block text-slate-700 font-serif mb-2 font-bold">
                          {isKorean ? "당신의 이야기를 들려주세요 (자유 형식)" : "Please share your story (Free format)"}
                        </label>
                        <textarea
                          rows={4}
                          value={userStory}
                          onChange={(e) => setUserStory(e.target.value)}
                          placeholder={isKorean ? "마음에 담아둔 이야기를 편하게 적어주세요..." : "Feel free to write what's on your mind..."}
                          className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none focus:ring-2 focus:ring-amber-300"
                        />
                      </div>

                      <div>
                        <label className="block text-slate-700 font-serif mb-2">{t.q1Name}</label>
                        <input
                          type="text"
                          value={formData.q1_name || ""}
                          onChange={(e) => handleFormChange("q1_name", e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none focus:ring-2 focus:ring-amber-300"
                        />
                      </div>

                      {selectedProduct.id !== "recovery" ? (
                        <>
                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q2Category}</label>
                            <select
                              value={formData.q2_category || ""}
                              onChange={(e) => handleFormChange("q2_category", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            >
                              <option value="">{t.q2CategoryPlaceholder}</option>
                              {t.q2CategoryOptions.map((label) => (
                                <option key={label} value={label}>{label}</option>
                              ))}
                            </select>
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q3Swallowed}</label>
                            <textarea
                              rows={3}
                              value={formData.q3_swallowed || ""}
                              onChange={(e) => handleFormChange("q3_swallowed", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q4Wants}</label>
                            <textarea
                              rows={2}
                              value={formData.q4_wants || ""}
                              onChange={(e) => handleFormChange("q4_wants", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q5Avoid}</label>
                            <input
                              type="text"
                              value={formData.q5_avoid || ""}
                              onChange={(e) => handleFormChange("q5_avoid", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q6Comfort}</label>
                            <input
                              type="text"
                              value={formData.q6_comfort || ""}
                              onChange={(e) => handleFormChange("q6_comfort", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.q7Wish}</label>
                            <textarea
                              rows={2}
                              value={formData.q7_wish || ""}
                              onChange={(e) => handleFormChange("q7_wish", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>
                        </>
                      ) : (
                        <>
                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ2Core}</label>
                            <textarea
                              rows={3}
                              value={formData.q2_core || ""}
                              onChange={(e) => handleFormChange("q2_core", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ3Breakdown}</label>
                            <textarea
                              rows={3}
                              value={formData.q3_breakdown || ""}
                              onChange={(e) => handleFormChange("q3_breakdown", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ4Wish}</label>
                            <textarea
                              rows={2}
                              value={formData.q4_wish || ""}
                              onChange={(e) => handleFormChange("q4_wish", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ5Time}</label>
                            <input
                              type="text"
                              value={formData.q5_time || ""}
                              onChange={(e) => handleFormChange("q5_time", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ6Action}</label>
                            <input
                              type="text"
                              value={formData.q6_action || ""}
                              onChange={(e) => handleFormChange("q6_action", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>

                          <div>
                            <label className="block text-slate-700 font-serif mb-2">{t.recoveryQ7Support}</label>
                            <textarea
                              rows={2}
                              value={formData.q7_support || ""}
                              onChange={(e) => handleFormChange("q7_support", e.target.value)}
                              className="w-full rounded-xl border border-slate-200 bg-white p-4 font-serif outline-none"
                            />
                          </div>
                        </>
                      )}
                    </>
                  )}
                </div>
                
                <div className="flex justify-between items-center mt-6">
                  <span className="text-xs text-slate-400 font-sans">
                    {Object.values(formData).filter((value) => value.trim().length > 0).length} / 7 {t.questionsCompleted}
                  </span>
                  
                  <button
                    onClick={handleFormSubmit}
                    className="px-8 py-3.5 bg-slate-800 text-white rounded-full font-serif text-lg hover:bg-slate-700 transition-all flex items-center shadow-md hover:shadow-lg transform hover:-translate-y-0.5 duration-200 active:scale-95 cursor-pointer"
                  >
                    {t.nextStep}
                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            {/* 2. 처방 티어 선택 (5 Tiers Grid matching test.html) */}
            {view === "tier" && (
              <div className="flex flex-col items-center w-full mt-4 animate-fade-in">
                <h2 className="font-serif text-2xl text-slate-700 mb-8 text-center font-bold">{t.selectTier}</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-3xl">
                  {TIERS.map((tier) => (
                    <div
                      key={tier.id}
                      onClick={() => handleSelectTier(tier)}
                      className={`relative bg-white/85 backdrop-blur-md rounded-2xl p-8 text-center border transition-all duration-300 cursor-pointer shadow-layered hover:shadow-layered-hover hover:-translate-y-1 ${
                        tier.popular ? "border-amber-300 bg-amber-50/20" : "border-white"
                      }`}
                    >
                      {tier.popular && (
                        <div className="absolute top-0 right-0 bg-amber-100 text-amber-700 text-xs px-3 py-1 rounded-bl-lg rounded-tr-2xl font-bold font-sans">
                          {t.popular}
                        </div>
                      )}
                      <h3 className="font-serif text-xl font-bold text-slate-800 mb-2">{t.tierNames[tier.id as keyof typeof t.tierNames]}</h3>
                      <p className="text-slate-500 text-sm mb-6 leading-relaxed min-h-[40px] flex items-center justify-center font-serif">{t.tierDescriptions[tier.id as keyof typeof t.tierDescriptions]}</p>
                      
                      <span className={`text-sm px-4 py-2 rounded-full font-medium ${
                        tier.priceVal === 0 
                          ? "text-emerald-600 border border-emerald-200 bg-emerald-50" 
                          : "text-amber-700 border border-amber-200 bg-amber-50/50 font-bold"
                      }`}>
                        {t.tierPriceText[tier.id as keyof typeof t.tierPriceText]}
                      </span>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={() => setView("input")}
                  className="mt-10 text-sm text-slate-400 hover:text-slate-600 underline underline-offset-4 font-sans cursor-pointer"
                >
                  {t.goBack}
                </button>
              </div>
            )}

            {/* 3. 결제 모듈 */}
            {view === "payment" && selectedProduct && (
              <div className="flex flex-col items-center w-full max-w-md mt-6 animate-fade-in bg-white/80 backdrop-blur-md rounded-2xl p-8 text-center border border-amber-100 shadow-layered">
                <h3 className="font-serif text-2xl text-slate-800 mb-2 font-bold">
                  {t.tierNames[selectedProduct.id as keyof typeof t.tierNames]} {t.paymentSuffix}
                </h3>
                <p className="text-slate-500 text-sm mb-8 font-serif">
                  {t.paymentDesc}
                </p>
                
                {/* 🎁 선물 패키지 정보 입력 (결제창 상단 노출) */}
                {selectedProduct.id === "gift" && (
                  <div className="w-full text-left mb-6 space-y-4 animate-fade-in">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 font-sans">
                        {t.giftRecipientLabel}
                      </label>
                      <input
                        type="text"
                        value={giftRecipient}
                        onChange={(e) => setGiftRecipient(e.target.value)}
                        placeholder={t.giftRecipientPlaceholder}
                        className="block w-full rounded-xl border border-slate-200 bg-white p-3.5 text-slate-800 text-sm placeholder:text-slate-400 font-serif outline-none focus:ring-2 focus:ring-amber-200 transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5 font-sans">
                        {t.giftRecipientEmailLabel}
                      </label>
                      <input
                        type="email"
                        value={giftRecipientEmail}
                        onChange={(e) => setGiftRecipientEmail(e.target.value)}
                        placeholder={t.giftRecipientEmailPlaceholder}
                        className="block w-full rounded-xl border border-slate-200 bg-white p-3.5 text-slate-800 text-sm placeholder:text-slate-400 font-serif outline-none focus:ring-2 focus:ring-amber-200 transition-all"
                      />
                    </div>
                  </div>
                )}

                <div className="w-full relative z-10">
                  <PayPalButtons
                    style={{ layout: "vertical", height: 48, shape: "rect", color: "black", label: "pay" }}
                    createOrder={(data, actions) => {
                      return actions.order.create({
                        intent: "CAPTURE",
                        purchase_units: [{ amount: { currency_code: "USD", value: selectedProduct.usd } }]
                      });
                    }}
                    onApprove={async (data, actions) => {
                      if (actions.order) {
                        await actions.order.capture();
                        generateLetter(selectedProduct.id as ProductType);
                      }
                    }}
                  />
                </div>

                <button
                  onClick={() => generateLetter(selectedProduct.id as ProductType)}
                  className="mt-6 w-full py-3 bg-slate-50 border border-slate-100 text-slate-500 rounded-xl text-xs font-sans hover:bg-slate-100 transition-colors active:scale-95 cursor-pointer font-medium"
                >
                  {t.testPaymentBypass}
                </button>
                
                <button
                  onClick={() => setView("tier")}
                  className="mt-6 text-sm text-slate-400 hover:text-slate-600 underline underline-offset-4 font-sans cursor-pointer"
                >
                  {t.goBack}
                </button>
              </div>
            )}

            {/* 4. 로딩 화면 */}
            {view === "loading" && (
              <div className="flex flex-col items-center justify-center py-20 w-full animate-fade-in text-center">
                <div className="animate-spin mb-8 text-slate-300">
                  <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <p className="text-slate-500 font-serif italic text-lg animate-pulse">
                  {productType === "random" ? t.randomLoadingText : t.loadingText}
                </p>
              </div>
            )}

            {/* 5. 결과 화면 (엽서 & 리뷰) */}
            {view === "full" && (
              <div className="animate-fade-in w-full max-w-2xl mt-4 flex flex-col items-center z-10">
                
                {/* 1. 3D Envelope Opening Scene (Shows if envelope is closed) */}
                {!envelopeOpen && (
                  <div className="w-full flex flex-col items-center justify-center py-12 md:py-20 animate-fade-in">
                    <p className="text-amber-400 font-serif text-lg mb-6 animate-pulse tracking-wide text-center">
                      {isKorean ? "💌 당신을 위한 위로의 편지가 도착했습니다." : "💌 A comforting letter has arrived for you."}
                    </p>
                    
                    <div className="envelope-container w-full max-w-[480px] px-4">
                      <div className="envelope-wrapper flex items-center justify-center relative">
                        {/* Top Flap */}
                        <div className="envelope-flap" />
                        
                        {/* Front pocket with card inside */}
                        <div className="envelope-front-pocket flex flex-col items-center justify-end pb-8 p-8">
                          <div className="text-center font-serif text-slate-700 select-none">
                            <p className="text-[10px] tracking-widest uppercase opacity-50 mb-1">Ask Your Heart</p>
                            <h3 className="text-xl md:text-2xl font-bold tracking-tight font-serif text-slate-800">
                              {formData.q1_name || (isKorean ? "소중한 마음" : "Someone Special")} {isKorean ? "님" : ""}
                            </h3>
                            <p className="text-[9px] opacity-40 mt-3 tracking-wider">
                              {isKorean ? "보낸 이: 오영범 마스터" : "Sender: Master O.Y.B"}
                            </p>
                          </div>
                        </div>

                        {/* Wax Seal Button at the Center */}
                        <div className="absolute top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] z-10 flex flex-col items-center gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              const wrapper = document.querySelector(".envelope-wrapper");
                              if (wrapper) {
                                wrapper.classList.add("open");
                                setTimeout(() => {
                                  setEnvelopeOpen(true);
                                }, 1400); // Transitions to letter sheet after slide up
                              }
                            }}
                            className="wax-seal"
                            aria-label="Open envelope"
                          >
                            <div className="wax-seal-inner">心</div>
                          </button>
                          <span className="text-[10px] font-sans font-bold text-amber-500 tracking-wider animate-bounce select-none uppercase mt-1">
                            {isKorean ? "왁스 실을 클릭하여 열기" : "Click seal to open"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. Letter Content & Action Step & Review UI (Shows after envelope is opened) */}
                {envelopeOpen && (
                  <div className="w-full flex flex-col items-center animate-fade-in">
                    
                    {/* 무료 및 유료 전체 엽서용 PDF 다운로드 버튼 */}
                    {letterData && (
                      <button
                        id="download-pdf-btn"
                        onClick={handleDownloadPDF}
                        className="mb-6 px-6 py-3 bg-slate-800 text-white rounded-full font-serif text-sm tracking-wide hover:bg-slate-700 transition shadow-lg flex items-center gap-2 animate-fade-in z-20 active:scale-95 duration-150 cursor-pointer"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        {t.pdfDownloadLabel}
                      </button>
                    )}

                    {/* 다중 페이지 PDF 생성을 위한 숨겨진 페이지 렌더링 */}
                    {letterData && (
                      <div id="multi-page-pdf-root" className="fixed top-[-9999px] left-[-9999px]" aria-hidden="true">
                        <div className="pdf-page w-[210mm] h-[297mm] flex flex-col items-center justify-center bg-[#FDFBF7] p-20">
                          <h1 className="text-4xl font-serif text-slate-800 text-center">
                            {letterData.cover?.title || t.freeCardLabel}
                          </h1>
                          <h2 className="text-xl mt-8 text-slate-500 font-serif text-center">
                            {letterData.cover?.heart_name}
                          </h2>
                        </div>

                        {(!letterData.recovery_days || letterData.recovery_days.length === 0) && (
                          <>
                            {getPaginatedParagraphs().map((pageParas, pageIdx) => (
                              <div key={`pdf-body-page-${pageIdx}`} className="pdf-page w-[210mm] h-[297mm] bg-[#FDFBF7] p-24 flex flex-col justify-center font-serif leading-loose text-lg text-slate-700">
                                {pageParas.map((para, idx) => (
                                  <p key={`body-${idx}`} className="mb-6 text-justify">
                                    {para}
                                  </p>
                                ))}
                              </div>
                            ))}

                            <div className="pdf-page w-[210mm] h-[297mm] bg-[#FDFBF7] p-24 flex flex-col justify-center">
                              <h3 className="text-xl mb-6 font-serif text-slate-800 font-bold border-b border-amber-200 pb-2">{t.premiumSentenceHeader}</h3>
                              {letterData.page_sentences?.map((sentence, idx) => (
                                <p key={`s-${idx}`} className="mb-3 text-base font-serif text-slate-600 italic">“ {sentence} ”</p>
                              ))}

                              <h3 className="text-xl mt-8 mb-6 font-serif text-slate-800 font-bold border-b border-amber-200 pb-2">{t.premiumQuestionHeader}</h3>
                              {letterData.page_questions?.map((q, idx) => (
                                <p key={`q-${idx}`} className="mb-3 text-base font-serif text-slate-600">Q. {q}</p>
                              ))}

                              {letterData.page_action && (
                                <>
                                  <h3 className="text-xl mt-8 mb-4 font-serif text-slate-800 font-bold border-b border-amber-200 pb-2">{t.premiumActionHeader}</h3>
                                  <p className="text-base font-serif text-slate-600 bg-amber-50/50 p-4 rounded-xl border border-amber-100">{letterData.page_action}</p>
                                </>
                              )}
                            </div>
                          </>
                        )}

                        {letterData.recovery_days && letterData.recovery_days.map((dayData, idx) => (
                          <div key={`recovery-${idx}`} className="pdf-page w-[210mm] h-[297mm] bg-[#FDFBF7] p-20 flex flex-col justify-center">
                            <h2 className="text-3xl font-serif text-slate-800 mb-12">{dayData.day}{t.recoveryDayHeader}</h2>
                            <p className="font-serif leading-loose text-lg text-slate-700 whitespace-pre-wrap mb-16">{dayData.letter}</p>
                            <div className="mt-auto p-8 border border-slate-300 rounded-2xl bg-white/50">
                              <h3 className="text-xl mb-4 font-serif text-slate-800">{t.premiumActionHeader}</h3>
                              <p className="text-lg font-serif text-slate-600">{dayData.action}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {["free", "random"].includes(productType) ? (
                      <div
                        id="letter-container"
                        onClick={skipTyping}
                        className="deckled-letter-paper rounded-xl p-10 md:p-16 w-full mb-8 relative overflow-hidden cursor-pointer"
                      >
                        {/* 1. Static Unsplash Image Layer with GPU acceleration */}
                        <div
                          className="absolute inset-0 z-0 transition-all duration-1000 will-change-transform transform-gpu translate-z-0 bg-cover bg-center"
                          style={{
                            backgroundImage: `url('${bgUrl}')`,
                          }}
                        />
                        {/* 2. Glassmorphic Gradient Overlay Layer */}
                        <div className="absolute inset-0 z-0 bg-gradient-to-b from-white/85 to-white/95" />
                        {/* 3. Pure CSS 아날로그 red grid paper micro-texture Layer */}
                        <div 
                          className="absolute inset-0 z-0 pointer-events-none opacity-40 mix-blend-multiply" 
                          style={{
                            backgroundImage: `linear-gradient(90deg, rgba(220,50,50,0.03) 50%, transparent 50%), 
                                              linear-gradient(rgba(220,50,50,0.03) 50%, transparent 50%)`,
                            backgroundSize: '4px 4px'
                          }}
                        />
                        
                        {/* 4. Vintage Postage Stamp (Top-Right Decor) */}
                        <div className="absolute top-6 right-6 z-20 pointer-events-none no-print">
                          <div className="vintage-stamp">
                            <span className="text-[7px] font-sans font-bold text-[#b91c1c] tracking-widest uppercase">KOREA</span>
                            <div className="text-sm my-1 text-slate-600 font-serif">心</div>
                            <span className="text-[6px] font-sans text-slate-400">2026</span>
                          </div>
                        </div>

                        <div className="relative z-10">
                          <p className="text-xs font-bold tracking-widest text-slate-400 mb-10 border-b border-slate-200/50 pb-4 text-center uppercase font-sans">
                            {t.storyHeader}
                          </p>
                          
                          <div className={`font-serif min-h-[300px] whitespace-pre-wrap flex flex-col ${
                            productType === "random" 
                              ? "justify-center text-2xl md:text-[26px] text-center py-12 leading-relaxed break-keep font-semibold text-slate-800" 
                              : "text-lg md:text-xl leading-loose text-slate-700"
                          }`}>
                            {productType === "random" ? (
                              <div className="relative inline-block mx-auto max-w-2xl px-8 py-6">
                                <span className="absolute top-0 left-0 text-6xl text-slate-300/50 font-serif leading-none select-none pointer-events-none">“</span>
                                <span className="relative z-10">{typedText}</span>
                                {(!isTyping) && <span className="absolute -bottom-4 right-0 text-6xl text-slate-300/50 font-serif leading-none select-none pointer-events-none">”</span>}
                                {isTyping && <span className="inline-block w-1.5 h-6 md:h-8 bg-slate-400 ml-2 animate-pulse align-middle relative z-10" />}
                              </div>
                            ) : (
                              <div>
                                {typedText}
                                {isTyping && <span className="inline-block w-1.5 h-6 bg-slate-400 ml-2 animate-pulse align-middle" />}
                              </div>
                            )}
                          </div>

                          {/* Master's Vintage Signature Signoff */}
                          {(!isTyping || view === "full") && (
                            <div className="mt-12 border-t border-slate-200/50 pt-6 flex flex-col items-end gap-1 select-none">
                              <p className="text-[11px] text-slate-400 font-sans italic">Warm regards,</p>
                              <h4 className="text-xl md:text-2xl font-serif text-slate-800 font-bold" style={{ fontFamily: "var(--font-serif), serif" }}>
                                Master 오영범
                              </h4>
                              {/* Instagram UGC Logo & Global Text */}
                              <div className="mt-2 flex items-center gap-1.5 text-slate-400 hover:text-slate-500 transition-colors text-xs font-sans">
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
                                <span>@young_beom_oh</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="w-full flex flex-col items-center animate-fade-in mb-8 px-4 sm:px-0">
                        {/* 프리미엄 웹 뷰어 컨테이너 (Premium Handcrafted Letter Sheet) */}
                        <div className="w-full max-w-2xl deckled-letter-paper rounded-[32px] p-10 md:p-16 mb-8 text-left overflow-hidden relative">
                          
                          {/* Vintage Postage Stamp (Top-Right Decor) */}
                          <div className="absolute top-6 right-6 z-20 pointer-events-none no-print">
                            <div className="vintage-stamp">
                              <span className="text-[7px] font-sans font-bold text-[#b91c1c] tracking-widest uppercase">KOREA</span>
                              <div className="text-sm my-1 text-slate-600 font-serif">心</div>
                              <span className="text-[6px] font-sans text-slate-400">2026</span>
                            </div>
                          </div>

                          <div className="text-center mb-14 border-b border-slate-200/60 pb-10">
                            <h1 className="text-3xl md:text-5xl font-serif text-slate-900 mb-4 tracking-tight leading-tight">{letterData?.cover?.title || t.freeCardLabel}</h1>
                            <p className="mx-auto max-w-xl text-base md:text-lg text-slate-500 font-serif leading-relaxed">{letterData?.cover?.heart_name}</p>
                          </div>

                          {(!letterData?.recovery_days || letterData.recovery_days.length === 0) ? (
                            <div className="font-serif leading-relaxed text-[1.02rem] md:text-lg text-slate-700 space-y-8">
                              {(letterData?.page_letter_paragraphs?.length ? letterData.page_letter_paragraphs : [letterData?.letter || ""]).map((para, idx) => (
                                <p key={`web-para-${idx}`} className="mb-8 first:mt-0 text-justify tracking-[0.01em]">{para}</p>
                              ))}
                              
                              <div className="mt-16 bg-white/90 backdrop-blur-[1px] p-8 rounded-[32px] border border-amber-100/60 shadow-[inset_0_1px_0_rgba(255,255,255,0.8),0_25px_60px_rgba(15,23,42,0.08)]">
                                <h3 className="text-2xl mb-6 font-serif text-slate-900 font-semibold border-b border-amber-100 pb-3 inline-block">오래 간직할 문장</h3>
                                {letterData?.page_sentences?.map((sentence, idx) => (
                                  <p key={`web-s-${idx}`} className="mb-4 text-slate-600 text-[0.98rem] leading-8">"{sentence}"</p>
                                ))}
                                
                                <h3 className="text-2xl mt-12 mb-6 font-serif text-slate-900 font-semibold border-b border-amber-100 pb-3 inline-block">나에게 묻는 질문</h3>
                                {letterData?.page_questions?.map((q, idx) => (
                                  <p key={`web-q-${idx}`} className="mb-4 text-slate-600 text-[0.98rem] leading-8">Q. {q}</p>
                                ))}

                                {letterData?.page_action && (
                                  <>
                                    <h3 className="text-2xl mt-12 mb-6 font-serif text-slate-900 font-semibold border-b border-amber-100 pb-3 inline-block">{t.premiumActionHeader}</h3>
                                    <p className="text-slate-600 text-[0.99rem] leading-7">{letterData.page_action}</p>
                                  </>
                                )}
                              </div>
                            </div>
                          ) : (
                            <div className="font-serif text-slate-700 space-y-16">
                              {letterData.recovery_days.map((dayData, idx) => (
                                <div key={`web-recovery-${idx}`} className="mb-16 last:mb-0 rounded-[32px] border border-slate-200/70 bg-white/90 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
                                  <h2 className="text-2xl md:text-3xl font-serif text-slate-900 mb-6 border-b border-slate-200/60 pb-3 inline-block">{dayData.day}일차 회복 편지</h2>
                                  <p className="leading-relaxed text-[1.01rem] md:text-lg whitespace-pre-wrap mb-10 text-slate-700">{dayData.letter}</p>
                                  <div className="bg-slate-50/95 p-6 rounded-[28px] border border-slate-200 shadow-[0_10px_40px_rgba(15,23,42,0.06)]">
                                    <h3 className="text-lg md:text-xl font-serif text-slate-900 mb-3 font-semibold">{t.premiumActionHeader}</h3>
                                    <p className="text-slate-600 text-[0.98rem] leading-7">{dayData.action}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Master's Premium Vintage Signature Signoff */}
                          <div className="mt-16 border-t border-slate-200/60 pt-8 flex flex-col items-end gap-1 select-none">
                            <p className="text-sm text-slate-400 font-sans italic">Warm regards,</p>
                            <h4 className="text-2xl font-serif text-slate-800 font-bold" style={{ fontFamily: "var(--font-serif), serif" }}>
                              Master 오영범
                            </h4>
                            <div className="mt-2 flex items-center gap-1.5 text-slate-400 text-xs font-sans">
                              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
                              <span>@young_beom_oh</span>
                            </div>
                          </div>

                        </div>
                        
                        {/* PDF 영구 소장 다운로드 버튼 */}
                        <button
                          id="download-pdf-btn"
                          onClick={handleDownloadPDF}
                          className="px-12 py-4 bg-slate-950 text-slate-200 rounded-full font-serif text-base md:text-lg tracking-[0.02em] hover:bg-slate-800 hover:text-white transition duration-200 shadow-2xl flex items-center gap-3 animate-fade-in z-20 active:scale-95 cursor-pointer border border-slate-800"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          {t.pdfPermanentLabel}
                        </button>
                      </div>
                    )}

                {/* [추가] 별점 및 리뷰 남기기 UI (하이엔드 미니멀리즘 디자인) */}
                <div className="w-full bg-white rounded-[32px] p-8 md:p-10 border border-slate-50 shadow-layered text-center animate-fade-in mb-8 no-print z-10">
                  <h4 className="font-serif text-xl md:text-2xl text-slate-800 mb-2 font-semibold">
                    {t.reviewTitle}
                  </h4>
                  <p className="text-slate-400 text-sm mb-6">
                    {t.reviewSubtitle}
                  </p>
                  
                  {!reviewSubmitted ? (
                    <form onSubmit={handleReviewSubmit} className="flex flex-col items-center">
                      <div className="flex gap-2 justify-center mb-6">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            type="button"
                            onClick={() => setRating(star)}
                            className={`text-3xl transition-colors cursor-pointer active:scale-90 duration-150 ${
                              star <= rating ? "text-amber-400" : "text-slate-200"
                            }`}
                          >
                            ★
                          </button>
                        ))}
                      </div>
                      <textarea
                        rows={5}
                        value={reviewText}
                        onChange={(e) => setReviewText(e.target.value)}
                        className="w-full rounded-xl bg-slate-50 border border-slate-100 shadow-inner p-4 text-slate-700 text-sm md:text-base mb-6 focus:ring-2 focus:ring-amber-200 focus:bg-white outline-none placeholder:text-slate-300 resize-none font-serif leading-relaxed"
                        style={{ minHeight: "150px", height: "150px" }}
                        placeholder={t.reviewPlaceholder}
                      />
                      <button
                        type="submit"
                        className="px-8 py-3.5 bg-slate-900 text-white rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shadow-md active:scale-95 duration-150 cursor-pointer"
                      >
                        {t.reviewSubmit}
                      </button>
                    </form>
                  ) : (
                    <div className="text-amber-600 text-sm font-medium bg-amber-50/50 border border-amber-100 px-6 py-4 rounded-2xl inline-block animate-fade-in">
                      {t.reviewSuccess}
                    </div>
                  )}
                </div>

                <footer className="mt-8 flex flex-col sm:flex-row gap-8 items-center justify-center no-print w-full">
                  <button
                    onClick={resetForm}
                    className="text-slate-400 hover:text-slate-600 flex items-center gap-2 text-sm transition-colors group font-serif cursor-pointer"
                  >
                    <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M10 19l-7-7m0 0l7-7m-7 7h18" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    {t.reset}
                  </button>
                </footer>
                  </div>
                )}
              </div>
            )}

          </main>
        </div>

        {/* Footer (Only on Input Form page) */}
        {view === "input" && (
          <footer className="w-full border-t border-amber-50/50 py-12 px-6 mt-auto no-print text-center">
            <p className="font-serif font-bold text-slate-800 text-lg mb-2">{t.footerBrand}</p>
            <p className="text-[10px] text-slate-400 tracking-[0.5em] uppercase">
              &copy; 2026 Master O.Y.B ALL RIGHTS RESERVED.
            </p>
          </footer>
        )}

      </div>
  );
}
