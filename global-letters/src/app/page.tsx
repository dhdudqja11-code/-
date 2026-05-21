"use client";

import { useState, useRef, useEffect } from "react";
import { PayPalButtons } from "@paypal/react-paypal-js";

type ProductType = "random" | "free" | "beta" | "deep" | "recovery";
type ViewState = "input" | "tier" | "payment" | "loading" | "full";

const TIERS = [
  { id: "random", name: "Random", desc: "오늘의 문장 (랜덤 뽑기)", priceText: "무료", priceVal: 0, usd: "0" },
  { id: "free", name: "Free", desc: "사연 기반 짧은 안부 편지", priceText: "무료 (일 1회)", priceVal: 0, usd: "0" },
  { id: "beta", name: "Beta", desc: "표준 처방전 및 심리 분석", priceText: "5,000원 ($3.99)", priceVal: 5000, usd: "3.99", popular: true },
  { id: "deep", name: "Deep", desc: "심층 심리 분석 및 행동 지침", priceText: "9,000원 ($6.99)", priceVal: 9000, usd: "6.99" },
  { id: "recovery", name: "Recovery", desc: "7일 집중 회복 여정 (연속 처방)", priceText: "29,000원 ($21.99)", priceVal: 29000, usd: "21.99" }
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
  "https://images.unsplash.com/photo-1483728642387-6c3ba6c6af81?q=80&w=1000&auto=format&fit=crop"
];

export default function Home() {
  const [view, setView] = useState<ViewState>("input");
  const [userStory, setUserStory] = useState("");
  const [productType, setProductType] = useState<ProductType>("free");
  const [typedText, setTypedText] = useState("");
  const [fullLetterText, setFullLetterText] = useState("");
  const [actionStep, setActionStep] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showAction, setShowAction] = useState(false);
  const [letterData, setLetterData] = useState<any>(null);
  const [drawCount, setDrawCount] = useState(0);
  const [bgUrl, setBgUrl] = useState("");
  const [mounted, setMounted] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<typeof TIERS[0] | null>(null);
  const [isKorean, setIsKorean] = useState(true);

  // 통계 및 리뷰용 상태 추가
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  // 🔒 타이핑 락 및 클로저 상태 수호용 Ref 객체
  const fullLetterRef = useRef("");
  const actionStepRef = useRef("");
  const isTypingRef = useRef(false);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined" && navigator.language) {
      setIsKorean(navigator.language.toLowerCase().includes('ko'));
    }
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

    // [추가] 방문자 트래픽 추적 백엔드 전송
    fetch("http://localhost:5000/api/track/visit", { method: "POST" })
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

  const handleStorySubmit = () => {
    const trimmed = userStory.trim();
    if (trimmed.length < 5) {
      alert("당신의 마음을 조금만 더 들려주세요. (5자 이상)");
      return;
    }
    setView("tier");
  };

  const handleSelectTier = (tier: typeof TIERS[0]) => {
    setProductType(tier.id as ProductType);
    if (tier.priceVal === 0) {
      if (tier.id === "random") {
        handleDrawGreeting();
      } else {
        generateLetter("free");
      }
    } else {
      setSelectedProduct(tier);
      setView("payment");
    }
  };

  const handleDrawGreeting = async () => {
    if (drawCount >= 999) {
      alert("오늘의 문장 뽑기는 하루에 999번까지만 가능합니다. 내일 다시 새로운 문장을 만나보세요! ✨");
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
      const response = await fetch("/api/generate-letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ story: userStory, productType: type }),
      });
      const data = await response.json();
      if (data.error) {
        alert(data.error);
        setView("tier");
        return;
      }
      setBgUrl(aestheticBackgrounds[Math.floor(Math.random() * aestheticBackgrounds.length)]);
      setLetterData(data);
      
      const legacyText = makeLegacyLetter(data);
      fullLetterRef.current = data.letter || legacyText;
      actionStepRef.current = data.action || data.page_action || "";
      
      setFullLetterText(data.letter || legacyText);
      setView("full");
      startTyping(data.letter || legacyText, data.action || data.page_action || "");
    } catch (error) {
      alert("편지 생성 중 오류가 발생했습니다.");
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
      await fetch("http://localhost:5000/api/track/review", {
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
    setView("input");
    setSelectedProduct(null);
    
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
      downloadBtn.innerHTML = "💌 PDF 저장 중...";
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
        script.onerror = (e) => reject(new Error("PDF 인쇄 라이브러리(Pro) 로드 실패: " + e));
        document.head.appendChild(script);
      });
    };

    try {
      const proEngine = await forceLoadProEngine();
      const jsPDF = (window as any).jsPDF || ((window as any).jspdf ? (window as any).jspdf.jsPDF : null);
      if (!jsPDF) {
        throw new Error("PDF 구성 파일(jsPDF)이 아직 로드되지 않았습니다.");
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
      alert("PDF 생성 중 오류가 발생했습니다.\n\n오류 내용: " + (err?.message || err));
    } finally {
      if (downloadBtn) {
        downloadBtn.innerHTML = originalText || "나만의 엽서 간직하기 (PDF)";
        (downloadBtn as any).disabled = false;
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-[#fdfbf7] relative selection:bg-amber-100 overflow-x-hidden font-serif">

        <div className="w-full max-w-4xl px-4 sm:px-6 py-12 md:py-16 flex flex-col items-center">
          
          {/* Header (Hidden on result view) */}
          {view !== "full" && (
            <header className="text-center mb-10 w-full max-w-3xl animate-fade-in transition-opacity duration-700">
              <h1 className="font-serif text-4xl md:text-5xl font-bold text-slate-800 mb-4 tracking-tight leading-tight">
                마음을 묻다
              </h1>
              <p className="text-slate-500 text-lg font-serif">
                당신의 짐을 잠시 내려놓으세요. 따뜻한 편지로 답해드립니다.
              </p>
            </header>
          )}

          <main className="w-full max-w-4xl relative flex flex-col items-center">
            
            {/* 1. 사연 입력창 */}
            {view === "input" && (
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-8 md:p-12 w-full max-w-4xl border border-white shadow-layered transition-all duration-500 animate-fade-in">
                <style dangerouslySetInnerHTML={{__html: `
                  #user-story {
                    height: 450px !important;
                    min-height: 450px !important;
                  }
                `}} />
                <textarea
                  id="user-story"
                  value={userStory}
                  onChange={(e) => setUserStory(e.target.value)}
                  maxLength={2000}
                  className="block w-full rounded-xl border border-slate-200 bg-white/60 p-6 text-slate-800 shadow-inner sm:text-lg transition-colors placeholder:text-slate-400 font-serif leading-relaxed outline-none focus:ring-2 focus:ring-slate-300 focus:bg-white focus:border-slate-300"
                  style={{ minHeight: "450px", height: "450px" }}
                  placeholder="요즘 마음이 어떠신가요? 편안하게 당신의 이야기를 들려주세요..."
                />
                
                <div className="flex justify-between items-center mt-6">
                  <span className="text-xs text-slate-400 font-sans">
                    {userStory.length} / 2000
                  </span>
                  
                  <button
                    onClick={handleStorySubmit}
                    className="px-8 py-3.5 bg-slate-800 text-white rounded-full font-serif text-lg hover:bg-slate-700 transition-all flex items-center shadow-md hover:shadow-lg transform hover:-translate-y-0.5 duration-200 active:scale-95 cursor-pointer"
                  >
                    사연 보내기
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
                <h2 className="font-serif text-2xl text-slate-700 mb-8 text-center font-bold">어떤 처방을 원하시나요?</h2>
                
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
                          인기
                        </div>
                      )}
                      <h3 className="font-serif text-xl font-bold text-slate-800 mb-2">{tier.name}</h3>
                      <p className="text-slate-500 text-sm mb-6 leading-relaxed min-h-[40px] flex items-center justify-center font-serif">{tier.desc}</p>
                      
                      <span className={`text-sm px-4 py-2 rounded-full font-medium ${
                        tier.priceVal === 0 
                          ? "text-emerald-600 border border-emerald-200 bg-emerald-50" 
                          : "text-amber-700 border border-amber-200 bg-amber-50/50 font-bold"
                      }`}>
                        {tier.priceText}
                      </span>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={() => setView("input")}
                  className="mt-10 text-sm text-slate-400 hover:text-slate-600 underline underline-offset-4 font-sans cursor-pointer"
                >
                  뒤로 가기
                </button>
              </div>
            )}

            {/* 3. 결제 모듈 */}
            {view === "payment" && selectedProduct && (
              <div className="flex flex-col items-center w-full max-w-md mt-6 animate-fade-in bg-white/80 backdrop-blur-md rounded-2xl p-8 text-center border border-amber-100 shadow-layered">
                <h3 className="font-serif text-2xl text-slate-800 mb-2 font-bold">
                  {selectedProduct.name} 처방전 결제
                </h3>
                <p className="text-slate-500 text-sm mb-8 font-serif">
                  결제를 완료하시면 마스터 오영범의 따뜻한 편지가 즉시 작성됩니다.
                </p>
                
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
                
                {/* 테스트용 간편 모의결제 우회 버튼 */}
                <button
                  onClick={() => generateLetter(selectedProduct.id as ProductType)}
                  className="mt-6 w-full py-3 bg-slate-50 border border-slate-100 text-slate-500 rounded-xl text-xs font-sans hover:bg-slate-100 transition-colors active:scale-95 cursor-pointer font-medium"
                >
                  ✨ [테스트용] 결제 우회 (개발자 전용)
                </button>
                
                <button
                  onClick={() => setView("tier")}
                  className="mt-6 text-sm text-slate-400 hover:text-slate-600 underline underline-offset-4 font-sans cursor-pointer"
                >
                  뒤로 가기
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
                  당신의 이야기를 깊이 들여다보고 있습니다...
                </p>
              </div>
            )}

            {/* 5. 결과 화면 (엽서 & 리뷰) */}
            {view === "full" && (
              <div className="animate-fade-in w-full max-w-2xl mt-4 flex flex-col items-center">
                
                {/* PDF 다운로드 버튼 */}
                <button
                  id="download-pdf-btn"
                  onClick={handleDownloadPDF}
                  className="mb-6 px-6 py-3 bg-slate-800 text-white rounded-full font-serif text-sm tracking-wide hover:bg-slate-700 transition shadow-lg flex items-center gap-2 animate-fade-in z-20 active:scale-95 duration-150 cursor-pointer"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  나만의 엽서 간직하기 (PDF)
                </button>

                {/* 다중 페이지 PDF 생성을 위한 숨겨진 페이지 렌더링 */}
                {letterData && (
                  <div
                    id="pdf-page-root"
                    className="fixed top-0 left-[-9999px] opacity-0 pointer-events-none"
                    aria-hidden="true"
                  >
                    <div className="pdf-page w-[210mm] h-[297mm] p-20 bg-[#FDFBF7] text-slate-800">
                      <div className="flex flex-col items-center justify-center h-full">
                        <h1 className="text-3xl font-serif font-bold mb-6 text-center">
                          {letterData.cover?.title || "당신을 위한 문장 처방전"}
                        </h1>
                        <h2 className="text-xl text-slate-500 text-center">
                          {letterData.cover?.heart_name || "괜찮은 척하느라 지친 마음에게"}
                        </h2>
                      </div>
                    </div>

                    <div className="pdf-page w-[210mm] h-[297mm] p-20 bg-[#FDFBF7] text-slate-800">
                      <div className="space-y-6 text-lg leading-relaxed font-serif">
                        {(Array.isArray(letterData.page_letter_paragraphs) ? letterData.page_letter_paragraphs : [letterData.letter || ""]).map((paragraph: string, idx: number) => (
                          <p key={`page-paragraph-${idx}`} className="mb-6">
                            {paragraph}
                          </p>
                        ))}
                      </div>
                    </div>

                    <div className="pdf-page w-[210mm] h-[297mm] p-20 bg-[#FDFBF7] text-slate-800">
                      <div className="space-y-8 font-serif">
                        {Array.isArray(letterData.page_sentences) && letterData.page_sentences.length > 0 && (
                          <div>
                            <h3 className="text-2xl font-semibold mb-6">오래 간직할 문장</h3>
                            {letterData.page_sentences.map((sentence: string, idx: number) => (
                              <p key={`sentence-${idx}`} className="mb-4 text-lg">
                                "{sentence}"
                              </p>
                            ))}
                          </div>
                        )}

                        {Array.isArray(letterData.page_questions) && letterData.page_questions.length > 0 && (
                          <div>
                            <h3 className="text-2xl font-semibold mb-6">나에게 묻는 질문</h3>
                            {letterData.page_questions.map((question: string, idx: number) => (
                              <p key={`question-${idx}`} className="mb-4 text-lg">
                                Q. {question}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {letterData.page_action && (
                      <div className="pdf-page w-[210mm] h-[297mm] p-20 bg-[#FDFBF7] text-slate-800">
                        <div className="h-full flex flex-col justify-center">
                          <h3 className="text-2xl font-semibold mb-8">오늘의 작은 행동</h3>
                          <p className="text-lg leading-relaxed">{letterData.page_action}</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* 격자 모눈 편지지 텍스처 엽서 */}
                <div
                  id="letter-container"
                  onClick={skipTyping}
                  className="rounded-2xl p-10 md:p-16 w-full mb-8 relative overflow-hidden shadow-layered border border-slate-100 cursor-pointer"
                >
                  {/* Background Image Layer with beautiful fine grids overlay */}
                  <div
                    className="absolute inset-0 z-0 transition-all duration-1000"
                    style={{
                      backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.95)), 
                                        linear-gradient(90deg, rgba(200,0,0,0.03) 50%, transparent 0), 
                                        linear-gradient(rgba(200,0,0,0.03) 50%, transparent 0), 
                                        url('${bgUrl}')`,
                      backgroundSize: 'cover, 3px 3px, 3px 3px, cover',
                      backgroundPosition: 'center'
                    }}
                  />
                  
                  <div className="relative z-10">
                    <p className="text-xs font-bold tracking-widest text-slate-400 mb-10 border-b border-slate-200/50 pb-4 text-center uppercase font-sans">
                      마음을 묻다
                    </p>
                    
                    <div className={`font-serif text-slate-700 min-h-[300px] whitespace-pre-wrap ${
                      productType === "random" ? "text-xl md:text-2xl text-center py-8 leading-loose" :
                      productType === "free" ? "text-lg md:text-xl leading-loose" :
                      productType === "beta" ? "text-lg md:text-xl leading-loose" :
                      productType === "deep" ? "text-base md:text-lg leading-relaxed" :
                      "text-sm md:text-base leading-relaxed" // recovery tier (very long)
                    }`}>
                      {typedText}
                      {isTyping && <span className="inline-block w-1.5 h-6 bg-slate-400 ml-2 animate-pulse" />}
                    </div>

                    {/* Instagram UGC Logo & Global Text */}
                    {(!isTyping || view === "full") && (
                      <div className="mt-12 flex items-center justify-end gap-1.5 text-slate-500 opacity-60 text-sm font-serif pt-4">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>
                        <span>@young_beom_oh</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* [추가] 별점 및 리뷰 남기기 UI (하이엔드 미니멀리즘 디자인) */}
                <div className="w-full bg-white rounded-[32px] p-8 md:p-10 border border-slate-50 shadow-layered text-center animate-fade-in mb-8 no-print z-10">
                  <h4 className="font-serif text-xl md:text-2xl text-slate-800 mb-2 font-semibold">
                    오늘의 편지가 위로가 되었나요?
                  </h4>
                  <p className="text-slate-400 text-sm mb-6">
                    소중한 피드백을 남겨주시면 대표님께 전달됩니다. ✨
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
                        placeholder="당신의 마음에 어떤 변화가 있었나요? 감상평을 편하게 남겨주세요..."
                      />
                      <button
                        type="submit"
                        className="px-8 py-3.5 bg-slate-900 text-white rounded-full text-sm font-medium hover:bg-slate-800 transition-colors shadow-md active:scale-95 duration-150 cursor-pointer"
                      >
                        리뷰 전송하기
                      </button>
                    </form>
                  ) : (
                    <div className="text-amber-600 text-sm font-medium bg-amber-50/50 border border-amber-100 px-6 py-4 rounded-2xl inline-block animate-fade-in">
                      리뷰가 성공적으로 전송되었습니다. 소중한 피드백 감사합니다! 💛
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
                    처음으로 돌아가기
                  </button>
                </footer>
              </div>
            )}

          </main>
        </div>

        {/* Footer (Only on Input Form page) */}
        {view === "input" && (
          <footer className="w-full border-t border-amber-50/50 py-12 px-6 mt-auto no-print text-center">
            <p className="font-serif font-bold text-slate-800 text-lg mb-2">마음을 묻다</p>
            <p className="text-[10px] text-slate-400 tracking-[0.5em] uppercase">
              &copy; 2026 Master O.Y.B ALL RIGHTS RESERVED.
            </p>
          </footer>
        )}

      </div>
  );
}
