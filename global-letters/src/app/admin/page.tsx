"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Heart, Shield, Sliders, Database, Mail, Terminal, Cpu, Layers, 
  Settings, AlertTriangle, TrendingDown, Send, History, Sparkles, 
  Clock, User, Server, RefreshCw, CheckCircle2, AlertCircle, Fingerprint, FileText
} from "lucide-react";

// Mock messages representing background AI agent activities
const MOCK_MESSAGES = [
  "[PA 영숙] 데일리 브리핑 기획 및 decisions.md RAG 최적화 점검 완료.",
  "[코다리] Gateway Audit Log - AuditBlock #73829 서명 검증 성공 (SHA-256).",
  "[오영범 작가] 사연 ID 'client_38' 감정 지표 스캔 (슬픔: 84%, 고독: 72%). 위로 편지 작성 시작.",
  "[trend_sniper] YouTube 급상승 힐링/위로 키워드 스캔 완료. '번아웃 극복', '자책 내려놓기' 추출.",
  "[reels_planner] 인스타그램 Reels 숏폼 대본 (60초 분량, 컷 분할 및 자막 매칭) 초안 기획 완료.",
  "[visual_director] 카드뉴스 썸네일 이미지 가이드라인 및 웜 톤 그라데이션 컬러 파라미터 세팅.",
  "[naver_publisher] 네이버 포스팅 발행 대기열 적재 완료. (상태: 대기 중)",
  "[instagram_publisher] 인스타그램 피드 이미지 해상도 매칭 검증 완료.",
  "[🛡️ 보안 관제] 침입 감시 모니터링 기동 - 비정상 세션 0건 감지 (안전)",
  "[현빈] 비즈니스 모델(BM) 분석 - 예상 회피 손실액($A_{LP}$) 가치 제안 데이터 동기화 완료.",
  "[마음 치유 엔진] 감정 프로파일링 로딩: '괜찮은 척하느라 지친 마음'에 매칭되는 문헌 가중치 적용.",
  "[PA 영숙] 마스터 뇌 지식 데이터베이스 동기화 완료. RAG 컨텍스트 용량 최적 상태 유지.",
  "[코다리] 5단계 IAG 인증 플로우 게이트웨이 무결성 검증 100% 그린 라이트.",
  "[오영범 작가] '7일 집중 회복 여정' Day 3: 자기 자비 처방전 PDF 템플릿 컴파일 완료.",
  "[🛡️ 보안 관제] CPU/GPU Thermal-Guard 쿨링 가드레일 가동 - 쓰로틀링 방어 모드 유지."
];

// 10대 에이전트 목록 정의
interface Agent {
  id: number;
  name: string;
  role: string;
  status: "ACTIVE" | "STANDBY" | "PROCESSING" | "SLEEP";
  priority: string;
}

const INITIAL_AGENTS: Agent[] = [
  { id: 1, name: "영숙 (PA)", role: "비서 · 피드백 피더", status: "STANDBY", priority: "Below Normal" },
  { id: 2, name: "코다리", role: "시니어 풀스택 엔지니어", status: "STANDBY", priority: "Normal" },
  { id: 3, name: "오영범 작가", role: "마음 치유 카피라이팅", status: "PROCESSING", priority: "Normal" },
  { id: 4, name: "현빈", role: "비즈니스 전략가", status: "STANDBY", priority: "Normal" },
  { id: 5, name: "visual_director", role: "비주얼 디렉터", status: "SLEEP", priority: "Normal" },
  { id: 6, name: "trend_sniper", role: "트렌드 분석가", status: "STANDBY", priority: "Below Normal" },
  { id: 7, name: "reels_planner", role: "숏폼 기획팀장", status: "SLEEP", priority: "Normal" },
  { id: 8, name: "naver_publisher", role: "네이버 발행 오토마타", status: "STANDBY", priority: "Below Normal" },
  { id: 9, name: "instagram_publisher", role: "인스타 발행 오토마타", status: "STANDBY", priority: "Below Normal" },
  { id: 10, name: "보안 관제 에이전트", role: "보안 & 원격 세션 복구", status: "ACTIVE", priority: "High" }
];

export default function AdminDashboard() {
  const [knowledgeText, setKnowledgeText] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [accumulatedDocs, setAccumulatedDocs] = useState([
    { id: 1, title: "본 계정 글.txt", date: "2026-05-14", tokens: "12,450" },
    { id: 2, title: "인생 방향 로드맵.md", date: "2026-05-10", tokens: "8,120" },
    { id: 3, title: "공방 통합 로드맵.md", date: "2026-04-28", tokens: "9,640" }
  ]);

  // Gifting queue and history states
  const [giftQueue, setGiftQueue] = useState<any[]>([]);
  const [giftHistory, setGiftHistory] = useState<any[]>([]);
  const [isLoadingGifts, setIsLoadingGifts] = useState(false);
  const [isSendingGifts, setIsSendingGifts] = useState(false);

  // Live Terminal Logs State
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // 10대 에이전트 상태
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);

  // Monte Carlo Risk Radar States (5 Risks)
  const [piiRisk, setPiiRisk] = useState<number>(3.2);
  const [auditRisk, setAuditRisk] = useState<number>(1.5);
  const [consentRisk, setConsentRisk] = useState<number>(2.4);
  const [sessionRisk, setSessionRisk] = useState<number>(1.8);
  const [trafficRisk, setTrafficRisk] = useState<number>(2.1);

  // Dynamic Telemetry States
  const [cpuTemp, setCpuTemp] = useState<number>(42.8);
  const [activeTokensRate, setActiveTokensRate] = useState<number>(1240);
  const [activeLoad, setActiveLoad] = useState<number>(14.2);

  // API 호출로 선물 대기열 정보 패치
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
    
    // 초기 터미널 로그 빌드
    const initialLogs = Array.from({ length: 6 }).map(() => {
      const time = new Date(Date.now() - Math.random() * 10000000).toLocaleTimeString("ko-KR");
      const msg = MOCK_MESSAGES[Math.floor(Math.random() * MOCK_MESSAGES.length)];
      return `[${time}] ${msg}`;
    });
    setTerminalLogs(initialLogs);
  }, []);

  // 1. 실시간 터미널 타이핑 업데이트 시뮬레이터
  useEffect(() => {
    const logInterval = setInterval(() => {
      const time = new Date().toLocaleTimeString("ko-KR");
      const randomMsg = MOCK_MESSAGES[Math.floor(Math.random() * MOCK_MESSAGES.length)];
      setTerminalLogs((prev) => {
        const next = [...prev, `[${time}] ${randomMsg}`];
        return next.slice(-40); // 최대 40개 유지
      });
      
      // AI Telemetry 미세 변경
      setCpuTemp((prev) => Math.max(38, Math.min(55, +(prev + (Math.random() - 0.5) * 2).toFixed(1))));
      setActiveTokensRate((prev) => Math.max(800, Math.min(2200, Math.floor(prev + (Math.random() - 0.5) * 300))));
      setActiveLoad((prev) => Math.max(5, Math.min(30, +(prev + (Math.random() - 0.5) * 4).toFixed(1))));
      
    }, 4500);

    return () => clearInterval(logInterval);
  }, []);

  // 2. 10대 에이전트 실시간 동작 상태 시뮬레이션
  useEffect(() => {
    const agentInterval = setInterval(() => {
      setAgents((prevAgents) => {
        return prevAgents.map((agent) => {
          // 보안 관제 에이전트는 항상 활성
          if (agent.id === 10) return agent;
          
          // 15% 확률로 상태 전이
          if (Math.random() < 0.18) {
            const statuses: ("ACTIVE" | "STANDBY" | "PROCESSING" | "SLEEP")[] = ["ACTIVE", "STANDBY", "PROCESSING", "SLEEP"];
            const nextStatus = statuses[Math.floor(Math.random() * statuses.length)];
            return { ...agent, status: nextStatus };
          }
          return agent;
        });
      });
    }, 3800);

    return () => clearInterval(agentInterval);
  }, []);

  // 터미널 스크롤 하단 고정
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [terminalLogs]);

  // 지식 업로드 API 실행
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
        id: Date.now(),
        title: `새로운 글 업데이트 (${new Date().toLocaleDateString()})`,
        date: new Date().toISOString().split("T")[0],
        tokens: Math.floor(knowledgeText.length * 1.5).toLocaleString()
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

  // 이메일 선물 일괄 전송 API 실행
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

  // 실시간 몬테카를로 기대 손실액(EL) 및 회피 가능 가치(Avoided Loss Potential - ALP) 계산
  // 최대 예상 리스크 잠재액 $350,000 USD
  const maxRiskPotential = 350000;
  const currentExpectedLoss = Math.floor(
    (piiRisk * 12.0 + auditRisk * 15.0 + consentRisk * 10.0 + sessionRisk * 18.0 + trafficRisk * 8.0) * 800
  );
  // Avoided Loss Potential (회피 가능 가치)
  const avoidedLossPotential = Math.max(0, maxRiskPotential - currentExpectedLoss);
  const isCriticalRisk = avoidedLossPotential < 150000;

  return (
    <div className="min-h-screen bg-[#090b11] text-slate-100 py-10 px-4 sm:px-6 lg:px-8 font-sans relative overflow-hidden">
      {/* Background glowing ambient nodes */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-amber-500/5 rounded-full filter blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-amber-500/5 rounded-full filter blur-[150px] pointer-events-none" />
      <div className="absolute top-[30%] right-[20%] w-[30%] h-[30%] bg-amber-600/5 rounded-full filter blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10 space-y-8">
        
        {/* Header - Holographic Admin HUD Header */}
        <header className="hud-panel rounded-2xl p-6 border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Spinning Golden Matrix Icon */}
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/40 flex items-center justify-center relative overflow-hidden shadow-[0_0_15px_rgba(245,158,11,0.15)]">
              <Cpu className="w-6 h-6 text-amber-500 animate-pulse" />
              <div className="absolute inset-0 border border-dashed border-amber-500/30 rounded-xl animate-spin-slow" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-amber-500 flex items-center gap-2 hud-glow-text font-serif">
                💌 마음을 묻다 통합 관리 센터
              </h1>
              <p className="text-xs text-slate-400 font-mono mt-1 tracking-wider uppercase">
                SYSTEM STATUS: <span className="text-emerald-500 font-bold animate-pulse">ONLINE</span> // MASTER ADMIN HUD v2.5
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button 
              onClick={fetchGifts}
              disabled={isLoadingGifts}
              className="bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 px-4 py-2.5 rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 active:scale-95"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoadingGifts ? 'animate-spin' : ''}`} />
              전송 대기열 동기화
            </button>
            
            {/* CPU Thermal Guard Priority Status Badge */}
            <div className="bg-[#0f1420] border border-amber-500/20 text-slate-300 px-4 py-2.5 rounded-xl text-xs font-mono flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              PRIORITY: BELOW_NORMAL (Thermal Guard Active)
            </div>
          </div>
        </header>

        {/* 3-Column Symmetrical Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* ================= COLUMN 1 ================= */}
          <div className="space-y-8">
            
            {/* Widget 1: Central Empathy Reactor Core */}
            <div className="hud-panel rounded-2xl p-6 flex flex-col items-center text-center">
              <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase mb-4 w-full text-left flex items-center justify-between border-b border-amber-500/10 pb-2">
                <span>[01] Empathy Core Reactor</span>
                <Sparkles className="w-3.5 h-3.5" />
              </h3>

              {/* Pulsing rotating graphic */}
              <div className="relative w-44 h-44 my-6 flex items-center justify-center">
                {/* Outermost rotating orbit */}
                <div className="absolute w-full h-full border border-dashed border-amber-500/20 rounded-full animate-spin-slow" />
                
                {/* Middle reverse-rotating orbit */}
                <div className="absolute w-36 h-36 border border-amber-500/30 rounded-full border-t-transparent border-b-transparent animate-spin-reverse-slow" />
                
                {/* Inner glowing core */}
                <div className="absolute w-24 h-24 rounded-full bg-amber-500/5 border-2 border-amber-500/50 flex items-center justify-center animate-pulse-reactor">
                  <Heart className="w-10 h-10 text-amber-500 fill-amber-500/20" />
                </div>
              </div>

              {/* Reactor Telemetry Metrics */}
              <div className="grid grid-cols-3 gap-2 w-full mt-4 font-mono text-center">
                <div className="bg-[#0f1420] border border-amber-500/10 p-2.5 rounded-xl">
                  <span className="block text-[10px] text-slate-400 uppercase">Core Temp</span>
                  <span className="text-sm font-bold text-amber-400">{cpuTemp}°C</span>
                </div>
                <div className="bg-[#0f1420] border border-amber-500/10 p-2.5 rounded-xl">
                  <span className="block text-[10px] text-slate-400 uppercase">Tokens/s</span>
                  <span className="text-sm font-bold text-amber-400">{activeTokensRate}</span>
                </div>
                <div className="bg-[#0f1420] border border-amber-500/10 p-2.5 rounded-xl">
                  <span className="block text-[10px] text-slate-400 uppercase">Active Load</span>
                  <span className="text-sm font-bold text-amber-400">{activeLoad}%</span>
                </div>
              </div>
            </div>

            {/* Widget 2: 10-Agent Diagnostics HUD */}
            <div className="hud-panel rounded-2xl p-6">
              <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase mb-4 flex items-center justify-between border-b border-amber-500/10 pb-2">
                <span>[02] 10-Agent Diagnostics</span>
                <Layers className="w-3.5 h-3.5" />
              </h3>

              <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1 hud-scrollbar">
                {agents.map((agent) => (
                  <div key={agent.id} className="bg-[#0f1420]/80 border border-amber-500/10 p-3 rounded-xl flex items-center justify-between text-xs font-mono hover:border-amber-500/30 transition-all">
                    <div className="flex items-center gap-2.5">
                      {/* Pulse Status LED */}
                      <span className={`w-2.5 h-2.5 rounded-full ${
                        agent.status === "PROCESSING" ? "bg-amber-400 animate-pulse" :
                        agent.status === "ACTIVE" ? "bg-emerald-500 animate-ping" :
                        agent.status === "SLEEP" ? "bg-slate-600" : "bg-sky-400"
                      }`} />
                      <div>
                        <span className="block font-semibold text-slate-200">{agent.name}</span>
                        <span className="text-[10px] text-slate-500">{agent.role}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`block text-[10px] font-bold ${
                        agent.status === "PROCESSING" ? "text-amber-400" :
                        agent.status === "ACTIVE" ? "text-emerald-400" :
                        agent.status === "SLEEP" ? "text-slate-500" : "text-sky-400"
                      }`}>{agent.status}</span>
                      <span className="text-[9px] text-slate-500">Pri: {agent.priority}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* ================= COLUMN 2 ================= */}
          <div className="space-y-8 lg:col-span-1">
            
            {/* Widget 3: Live Empathy Stream Terminal */}
            <div className="hud-panel rounded-2xl p-6 flex flex-col h-[340px]">
              <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase mb-3 flex items-center justify-between border-b border-amber-500/10 pb-2">
                <span>[03] Live Empathy Stream Terminal</span>
                <Terminal className="w-3.5 h-3.5" />
              </h3>

              <div className="flex-grow bg-[#05070a]/90 rounded-xl p-4 font-mono text-[11px] leading-relaxed text-amber-400/90 overflow-y-auto hud-scrollbar scanlines border border-amber-500/20 relative shadow-inner">
                <div className="space-y-2 relative z-10">
                  {terminalLogs.map((log, idx) => (
                    <div key={idx} className="whitespace-pre-wrap select-all selection:bg-amber-500/30 selection:text-white">
                      {log}
                    </div>
                  ))}
                  <div ref={terminalEndRef} />
                </div>
              </div>
            </div>

            {/* Widget 4: Knowledge Base Injector */}
            <div className="hud-panel rounded-2xl p-6">
              <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase mb-3 flex items-center justify-between border-b border-amber-500/10 pb-2">
                <span>[04] Knowledge Base Injector</span>
                <Database className="w-3.5 h-3.5" />
              </h3>
              <p className="text-[11px] text-slate-400 mb-4 leading-relaxed font-serif">
                인스타그램/블로그에 올린 대표님의 글과 위로 철학을 입력창에 주입하세요. 
                AI 마스터가 해당 텍스트를 분석하여 향후 고민 해소 편지 처방에 녹여냅니다.
              </p>

              <textarea
                rows={5}
                value={knowledgeText}
                onChange={(e) => setKnowledgeText(e.target.value)}
                className="w-full bg-[#07090f] border border-amber-500/20 rounded-xl p-4 text-slate-200 text-sm font-serif leading-relaxed focus:ring-1 focus:ring-amber-500 focus:border-amber-500 outline-none transition-all resize-none shadow-inner"
                placeholder="이곳에 AI 상담 마스터에게 이식할 따뜻한 문장을 마음껏 주입하세요..."
              />

              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleSaveKnowledge}
                  disabled={isSaving}
                  className={`w-full sm:w-auto px-6 py-3 rounded-xl font-medium text-xs text-slate-900 border font-bold shadow-sm transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                    isSaving 
                      ? "bg-amber-500/50 border-amber-500/30 text-amber-100 cursor-not-allowed" 
                      : "bg-amber-500 border-amber-500 hover:bg-amber-400 hover:shadow-[0_0_15px_rgba(245,158,11,0.4)] active:scale-95 duration-150"
                  }`}
                >
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-slate-900"></div>
                      지식 주입 중...
                    </>
                  ) : (
                    <>
                      <Database className="w-3.5 h-3.5" />
                      마스터 지식 DB에 이식 (RAG 학습)
                    </>
                  )}
                </button>
              </div>
            </div>

          </div>

          {/* ================= COLUMN 3 ================= */}
          <div className="space-y-8">
            
            {/* Widget 5: Monte Carlo Risk Radar */}
            <div className={`hud-panel rounded-2xl p-6 transition-all duration-500 border ${
              isCriticalRisk ? "border-rose-500/30 shadow-[0_0_20px_rgba(239,68,68,0.1)]" : "border-amber-500/20"
            }`}>
              <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase mb-4 flex items-center justify-between border-b border-amber-500/10 pb-2">
                <span>[05] Monte Carlo Risk Radar</span>
                <Sliders className="w-3.5 h-3.5" />
              </h3>

              {/* Dynamic Avoided Loss Gauge */}
              <div className="bg-[#0f1420] border border-amber-500/10 rounded-xl p-4 mb-5 text-center relative overflow-hidden">
                <span className="text-[10px] text-slate-400 uppercase font-mono block mb-1">{"Avoided Loss Potential ($A_{LP}$)"}</span>
                <span className={`text-2xl font-black font-mono tracking-tight hud-glow-text ${
                  isCriticalRisk ? "text-rose-500" : "text-amber-500"
                }`}>
                  ${avoidedLossPotential.toLocaleString()} USD
                </span>
                
                {/* Status Indicator */}
                <div className="mt-2 flex items-center justify-center gap-1.5 text-[9px] font-mono">
                  {isCriticalRisk ? (
                    <span className="text-rose-400 font-bold uppercase flex items-center gap-1 animate-pulse">
                      <AlertTriangle className="w-3 h-3 text-rose-500" /> CRITICAL RISK GUARD WARNING
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-semibold uppercase flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" /> SYSTEM FINANCIAL SECURITY PASS
                    </span>
                  )}
                </div>
              </div>

              {/* 5 Risks Sliders */}
              <div className="space-y-3.5 font-mono text-xs text-slate-300">
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>PII Leakage Risk</span>
                    <span className="font-bold text-amber-400">{piiRisk} / 10</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.1"
                    value={piiRisk}
                    onChange={(e) => setPiiRisk(+e.target.value)}
                    className="w-full accent-amber-500 bg-[#07090f] rounded-lg h-1 appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>Audit Log Absence Risk</span>
                    <span className="font-bold text-amber-400">{auditRisk} / 10</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.1"
                    value={auditRisk}
                    onChange={(e) => setAuditRisk(+e.target.value)}
                    className="w-full accent-amber-500 bg-[#07090f] rounded-lg h-1 appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>Consent Failure Risk</span>
                    <span className="font-bold text-amber-400">{consentRisk} / 10</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.1"
                    value={consentRisk}
                    onChange={(e) => setConsentRisk(+e.target.value)}
                    className="w-full accent-amber-500 bg-[#07090f] rounded-lg h-1 appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>Session Security Risk</span>
                    <span className="font-bold text-amber-400">{sessionRisk} / 10</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.1"
                    value={sessionRisk}
                    onChange={(e) => setSessionRisk(+e.target.value)}
                    className="w-full accent-amber-500 bg-[#07090f] rounded-lg h-1 appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span>Traffic Surge Risk</span>
                    <span className="font-bold text-amber-400">{trafficRisk} / 10</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.1"
                    value={trafficRisk}
                    onChange={(e) => setTrafficRisk(+e.target.value)}
                    className="w-full accent-amber-500 bg-[#07090f] rounded-lg h-1 appearance-none cursor-pointer"
                  />
                </div>
              </div>
            </div>

            {/* Widget 6: Gift Dispatch Queue & History */}
            <div className="hud-panel rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2 border-b border-amber-500/10 pb-3">
                <h3 className="text-xs font-mono text-amber-500/70 tracking-widest uppercase flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" />
                  <span>[06] Gift Dispatch Console</span>
                </h3>
                
                <button
                  onClick={handleDispatchGifts}
                  disabled={isSendingGifts || giftQueue.length === 0}
                  className={`px-3 py-1.5 rounded-lg font-bold text-[10px] flex items-center justify-center gap-1 shadow-sm transition-all cursor-pointer ${
                    isSendingGifts || giftQueue.length === 0
                      ? "bg-slate-800 border border-slate-700/50 text-slate-500 cursor-not-allowed opacity-80"
                      : "bg-amber-500 border border-amber-500 hover:bg-amber-400 hover:shadow-[0_0_10px_rgba(245,158,11,0.3)] active:scale-95 text-slate-900 duration-150"
                  }`}
                >
                  {isSendingGifts ? "전송 중..." : "일괄 발송 실행"}
                </button>
              </div>

              {isLoadingGifts ? (
                <div className="py-10 flex flex-col items-center justify-center text-slate-400">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500 mb-2"></div>
                  <p className="text-[10px] font-mono text-slate-500">대기열 탐색 중...</p>
                </div>
              ) : giftQueue.length === 0 ? (
                <div className="py-8 text-center border border-dashed border-amber-500/10 rounded-xl bg-[#0f1420]/30">
                  <p className="text-2xl mb-1.5">📭</p>
                  <p className="text-slate-400 text-xs font-medium font-serif">오늘 대기중인 선물 예약 건이 없습니다.</p>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">유저가 메인 엽서에서 선물하기 결제 시 여기에 적재됩니다.</p>
                </div>
              ) : (
                <div className="overflow-y-auto max-h-[140px] hud-scrollbar border border-amber-500/10 rounded-xl bg-[#07090f]/50">
                  <table className="min-w-full divide-y divide-amber-500/10 text-[10px] font-mono text-slate-300">
                    <thead className="bg-[#0f1420] text-amber-500/80 sticky top-0">
                      <tr className="text-left uppercase">
                        <th className="p-2">Sender</th>
                        <th className="p-2">Receiver</th>
                        <th className="p-2">Prescription</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-amber-500/10">
                      {giftQueue.map((item) => (
                        <tr key={item.id} className="hover:bg-amber-500/5 transition-colors">
                          <td className="p-2 font-semibold text-slate-200">{item.senderName}</td>
                          <td className="p-2 text-slate-400">{item.recipientName}</td>
                          <td className="p-2 max-w-[120px] truncate italic font-serif">{item.letterData?.cover?.title || "문장 처방전"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Dispatch history block */}
              <div className="mt-4 pt-4 border-t border-amber-500/10">
                <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1 mb-2">
                  <History className="w-3 h-3 text-slate-500" /> 최근 전송 성공 이력 (최대 3건)
                </span>
                {giftHistory.length === 0 ? (
                  <p className="text-[10px] text-slate-500 font-mono italic">발송 이력이 비어 있습니다.</p>
                ) : (
                  <ul className="space-y-1.5 font-mono text-[9px] text-slate-400">
                    {giftHistory.slice().reverse().slice(0, 3).map((item, idx) => (
                      <li key={idx} className="bg-[#0f1420]/50 p-2 rounded border border-amber-500/5 flex justify-between items-center">
                        <span className="truncate pr-1 text-slate-300">{item.senderName} ➡️ {item.recipientName}</span>
                        <span className="text-[9px] font-bold text-emerald-400">SUCCESS</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

          </div>

        </div>

        {/* Bottom Section: Accumulated Knowledge stats (Serif Theme) */}
        <div className="hud-panel rounded-2xl p-6 grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          <div className="md:col-span-1 border-r border-amber-500/10 pr-6">
            <span className="text-xs font-mono text-amber-500/80 uppercase block mb-1">RAG Knowledge Base Storage</span>
            <h3 className="text-xl font-bold font-serif text-slate-200 flex items-center gap-2">
              <Database className="w-5 h-5 text-amber-500" />
              학습 완료된 작가 지식 풀
            </h3>
            <p className="text-xs text-slate-400 mt-2 font-serif leading-relaxed">
              대표님께서 업로드하신 모든 원본 텍스트와 생각의 단편들은 RAG 벡터 스토어에 구조화되어, 편지 생성 엔진의 고유 위계 매개변수로 융합 작동합니다.
            </p>
          </div>
          
          <div className="md:col-span-2 flex flex-wrap gap-4 overflow-x-auto py-2">
            {accumulatedDocs.map((doc) => (
              <div key={doc.id} className="bg-[#0f1420] border border-amber-500/10 hover:border-amber-500/30 p-3.5 rounded-xl text-xs font-mono w-56 flex flex-col justify-between transition-colors shadow-inner">
                <div className="flex justify-between items-start mb-2 gap-2">
                  <span className="font-semibold text-slate-200 truncate" title={doc.title}>{doc.title}</span>
                  <span className="text-[9px] text-slate-500 whitespace-nowrap">{doc.date}</span>
                </div>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" /> SYNCED
                  </span>
                  <span className="text-slate-400">{doc.tokens} Tokens</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
