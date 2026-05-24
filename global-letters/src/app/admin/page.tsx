"use client";

import { useState, useEffect } from "react";

export default function AdminDashboard() {
  const [knowledgeText, setKnowledgeText] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [accumulatedDocs, setAccumulatedDocs] = useState([
    { id: 1, title: "본 계정 글.txt", date: "2026-05-14", tokens: "12,450" },
  ]);

  // Gifting queue and history states
  const [giftQueue, setGiftQueue] = useState<any[]>([]);
  const [giftHistory, setGiftHistory] = useState<any[]>([]);
  const [isLoadingGifts, setIsLoadingGifts] = useState(false);
  const [isSendingGifts, setIsSendingGifts] = useState(false);

  const fetchGifts = async () => {
    setIsLoadingGifts(true);
    try {
      const response = await fetch("/api/send-gift?view=true");
      const data = await response.json();
      if (data.success) {
        setGiftQueue(data.queue || []);
        setGiftHistory(data.history || []);
      }
    } catch (error) {
      console.error("Failed to fetch gifts queue:", error);
    } finally {
      setIsLoadingGifts(false);
    }
  };

  useEffect(() => {
    fetchGifts();
  }, []);

  const handleSaveKnowledge = async () => {
    if (knowledgeText.trim().length < 10) {
      alert("학습시킬 글을 조금 더 길게 작성해 주세요.");
      return;
    }

    setIsSaving(true);
    
    try {
      const response = await fetch("/api/upload-knowledge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: knowledgeText }),
      });
      
      const data = await response.json();
      
      if (data.error) {
        alert(data.error);
        setIsSaving(false);
        return;
      }
      
      alert(`✨ ${data.message}`);
      
      const newDoc = {
        id: accumulatedDocs.length + 1,
        title: `새로운 글 업데이트 (${new Date().toLocaleDateString()})`,
        date: new Date().toISOString().split("T")[0],
        tokens: Math.floor(knowledgeText.length * 1.5).toString()
      };
      
      setAccumulatedDocs([newDoc, ...accumulatedDocs]);
      setKnowledgeText("");
    } catch (error) {
      console.error(error);
      alert("업로드 중 오류가 발생했습니다. 다시 시도해 주세요.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDispatchGifts = async () => {
    if (giftQueue.length === 0) {
      alert("전송할 대기 중인 편지가 없습니다.");
      return;
    }

    if (!confirm(`정말로 현재 대기 중인 ${giftQueue.length}개의 선물 편지를 모두 전송하시겠습니까?\n이 작업은 Nodemailer/Sandbox 메일 전송 모듈을 가동하여 즉시 발송합니다.`)) {
      return;
    }

    setIsSendingGifts(true);
    try {
      const response = await fetch("/api/send-gift");
      const data = await response.json();
      if (data.success) {
        alert(`✨ 성공적으로 ${data.count}개의 선물 엽서가 발송되었습니다!\n(전송 방식: ${data.mode})`);
        fetchGifts();
      } else {
        alert(`❌ 전송 중 오류 발생: ${data.error}`);
      }
    } catch (error) {
      console.error(error);
      alert("발송 중 오류가 발생했습니다.");
    } finally {
      setIsSendingGifts(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8 font-sans text-slate-800">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-5 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>💌</span> 마음을 묻다 통합 관리 센터
            </h1>
            <p className="text-sm text-slate-500 mt-2">
              대표님만의 글과 철학을 AI 상담사에게 누적 학습시키고, 일일 선물/결제 대기열을 일괄 전송 및 관리하는 공간입니다.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={fetchGifts}
              disabled={isLoadingGifts}
              className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 px-4 py-2 rounded-xl text-sm font-medium shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <svg className={`w-4 h-4 text-slate-500 ${isLoadingGifts ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H18.25" />
              </svg>
              새로고침
            </button>
            <div className="bg-amber-50 text-amber-700 px-4 py-2 rounded-xl text-sm font-semibold border border-amber-200 shadow-sm whitespace-nowrap">
              Master Admin Mode
            </div>
          </div>
        </header>

        {/* Section 1: AI Knowledge Base and Upload */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Left Column: Upload New Knowledge */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
              <h2 className="text-xl font-semibold mb-2 flex items-center">
                <svg className="w-5 h-5 mr-2 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                새로운 철학/위로 글 학습시키기
              </h2>
              <p className="text-sm text-slate-500 mb-6">
                인스타그램이나 블로그에 작성하신 대표님의 감성 글, 심리학적 깊은 성찰이 담긴 글들을 아래에 붙여넣어 주세요. 
                AI 상담사(오영범 마스터)가 이 고유한 문체와 위로 철학을 완벽하게 습득하여 다음 처방전 작성 시 핵심 기반으로 녹여냅니다.
              </p>
              
              <div className="relative">
                <textarea
                  rows={10}
                  value={knowledgeText}
                  onChange={(e) => setKnowledgeText(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-slate-700 focus:ring-2 focus:ring-amber-300 focus:border-amber-500 outline-none transition-all resize-none font-serif leading-relaxed"
                  placeholder="이곳에 학습시킬 새로운 위로의 글을 마음껏 붙여넣으세요..."
                />
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleSaveKnowledge}
                  disabled={isSaving}
                  className={`px-8 py-3.5 rounded-xl font-medium text-white shadow-sm transition-all flex items-center cursor-pointer ${
                    isSaving ? "bg-amber-400 cursor-not-allowed" : "bg-slate-900 hover:bg-slate-800 hover:shadow-md active:scale-98"
                  }`}
                >
                  {isSaving ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      AI가 대표님의 마음을 연구 중...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                      마스터 뇌 지식 저장소 업로드 (학습 실행)
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Accumulated Knowledge Stats */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 h-full flex flex-col">
              <h3 className="text-lg font-semibold mb-4 border-b border-slate-100 pb-3 flex items-center">
                <svg className="w-5 h-5 mr-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
                누적된 마스터 지식 데이터
              </h3>
              
              <ul className="space-y-4 overflow-y-auto flex-grow max-h-[300px]">
                {accumulatedDocs.map((doc) => (
                  <li key={doc.id} className="p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-slate-300 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-slate-800 text-sm truncate pr-2">{doc.title}</span>
                      <span className="text-xs text-slate-400 whitespace-nowrap">{doc.date}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-500">
                      <span className="flex items-center text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        성공적으로 동기화됨
                      </span>
                      <span>{doc.tokens} 토큰</span>
                    </div>
                  </li>
                ))}
              </ul>
              
              <div className="mt-6 pt-4 border-t border-slate-100 text-center">
                <p className="text-xs text-slate-400">
                  누적된 모든 글귀와 지식은 AI 상담사가 위로를 구성할 때 RAG 컨텍스트 모델링 기반으로 자동 융합됩니다.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Gifting Batch Dispatch Queue & History */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Gifting Queue list (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4 border-b border-slate-100 pb-5">
                <div>
                  <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <span>⏳</span> 오늘의 선물 배송/전송 대기열
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    결제된 선물 엽서들은 즉시 전송되지 않고 이 대기열에 안전하게 모여 그날 밤 일괄 전송됩니다.
                  </p>
                </div>
                <div>
                  <button
                    onClick={handleDispatchGifts}
                    disabled={isSendingGifts || giftQueue.length === 0}
                    className={`w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-white shadow-sm flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                      isSendingGifts || giftQueue.length === 0
                        ? "bg-slate-300 cursor-not-allowed opacity-80"
                        : "bg-amber-500 hover:bg-amber-600 hover:shadow-md active:scale-98"
                    }`}
                  >
                    {isSendingGifts ? (
                      <>
                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        일괄 전송 처리 중...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                        오늘의 선물 한꺼번에 일괄 전송하기
                      </>
                    )}
                  </button>
                </div>
              </div>

              {isLoadingGifts ? (
                <div className="py-20 flex flex-col items-center justify-center text-slate-400">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mb-4"></div>
                  <p className="text-sm">대기열 정보를 불러오는 중입니다...</p>
                </div>
              ) : giftQueue.length === 0 ? (
                <div className="py-16 text-center border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                  <p className="text-3xl mb-3">📭</p>
                  <p className="text-slate-500 text-sm font-medium">현재 새로 들어와서 발송 대기 중인 선물 예약 건이 없습니다.</p>
                  <p className="text-xs text-slate-400 mt-1">유저가 메인 엽서에서 선물하기 결제 시 이 대기열에 쌓이게 됩니다.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-100">
                    <thead>
                      <tr className="text-left text-xs font-bold text-slate-400 uppercase tracking-wider bg-slate-50 rounded-lg">
                        <th className="p-3">보낸 이</th>
                        <th className="p-3">받는 이</th>
                        <th className="p-3">수신 이메일</th>
                        <th className="p-3">처방전 타이틀</th>
                        <th className="p-3">접수 일시</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-sm text-slate-700 font-sans">
                      {giftQueue.map((item) => (
                        <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="p-3 font-semibold text-slate-800">{item.senderName}</td>
                          <td className="p-3 text-slate-600">{item.recipientName}</td>
                          <td className="p-3 font-mono text-xs text-slate-500">{item.recipientEmail}</td>
                          <td className="p-3 font-serif max-w-[150px] truncate">{item.letterData?.cover?.title || "문장 처방전"}</td>
                          <td className="p-3 text-slate-400 text-xs">{new Date(item.timestamp).toLocaleString("ko-KR")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Gifting History list (Right 1 col) */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
              <h3 className="text-lg font-semibold mb-4 border-b border-slate-100 pb-3 flex items-center">
                <svg className="w-5 h-5 mr-2 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                최근 전송 성공 이력
              </h3>

              {isLoadingGifts ? (
                <div className="py-12 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-slate-400"></div>
                </div>
              ) : giftHistory.length === 0 ? (
                <div className="py-10 text-center text-slate-400 flex-grow flex flex-col items-center justify-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                  <p className="text-sm">최근 발송 완료된 이력이 없습니다.</p>
                </div>
              ) : (
                <ul className="space-y-4 overflow-y-auto flex-grow max-h-[350px]">
                  {giftHistory.slice().reverse().map((item, idx) => (
                    <li key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-100 hover:border-slate-200 transition-colors text-xs">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="font-semibold text-slate-800">{item.senderName} ➡️ {item.recipientName}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.status === "SUCCESS" ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
                        }`}>{item.status}</span>
                      </div>
                      <p className="text-[10px] text-slate-400 truncate mb-1">Email: {item.recipientEmail}</p>
                      <p className="text-[9px] text-slate-400 text-right">발송일: {new Date(item.sentAt || item.timestamp).toLocaleString("ko-KR")}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
