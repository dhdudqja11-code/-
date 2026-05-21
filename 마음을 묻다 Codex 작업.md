# 🤖 Codex 프론트엔드 개편 작업 지시서 (마음을 묻다)

> **To. Codex (GitHub Copilot / Cursor AI)**
> 당신은 프론트엔드와 React/Next.js 환경에 정통한 최고 수준의 AI입니다. 백엔드 아키텍처와 AI 프롬프트는 이미 Antigravity에 의해 다중 페이지 전자책(PDF) 생성 방식으로 전면 개편되었습니다. 당신의 임무는 이 문서에 적힌 구체적인 코드와 가이드를 바탕으로 **`global-letters/src/app/page.tsx`의 프론트엔드 코드를 완벽하게 개편하는 것**입니다.

---

## 📝 작업 1: 백엔드 JSON 파싱 및 State 구조 변경
현재 프론트엔드는 AI로부터 단일 `letter` 문자열을 받고 있습니다. 하지만 백엔드 API(`generate-letter`)는 이제 아래와 같은 완벽한 다중 페이지용 JSON 구조체를 반환합니다.

### 1-1. `page.tsx`의 상태(State) 타입 업데이트
```tsx
// 기존에 string으로 받던 letter 상태를 아래와 같은 구조체 상태로 변경하세요.
interface LetterData {
  cover: { title: string; heart_name: string };
  page_letter_paragraphs: string[];
  page_sentences: string[];
  page_questions: string[];
  page_action: string;
}
const [letterData, setLetterData] = useState<LetterData | null>(null);
```

---

## 📝 작업 2: 유료 버전용 '다중 페이지 PDF DOM' 추가 (핵심)
엽서 한 장에 긴 글을 때려 넣으면 UI가 붕괴됩니다. 유료 버전(Beta, Deep 등)을 결제한 경우, 화면에 보이는 엽서 대신 **A4 크기의 숨겨진 DOM 요소 여러 장을 렌더링**해야 합니다.

### 2-1. 숨겨진 다중 페이지 루트 삽입
`page.tsx`의 최상단 래퍼 안쪽(가장 밖)에 아래 코드를 추가하십시오.
```tsx
{/* 인쇄 및 PDF 캡처 전용: 화면 밖으로 숨김 처리 */}
<div id="multi-page-pdf-root" className="fixed top-[-9999px] left-[-9999px]">
  {letterData && (
    <>
      {/* 1페이지: 표지 */}
      <div className="pdf-page w-[210mm] h-[297mm] flex flex-col items-center justify-center bg-[#FDFBF7] p-20">
        <h1 className="text-4xl font-serif text-slate-800">{letterData.cover?.title || "당신을 위한 문장 처방전"}</h1>
        <h2 className="text-xl mt-8 text-slate-500 font-serif">{letterData.cover?.heart_name}</h2>
      </div>

      {/* 2페이지: 본문 */}
      <div className="pdf-page w-[210mm] h-[297mm] bg-[#FDFBF7] p-20 flex flex-col justify-center">
        <div className="font-serif leading-loose text-lg text-slate-700">
          {letterData.page_letter_paragraphs?.map((para, idx) => (
            <p key={idx} className="mb-6">{para}</p>
          ))}
        </div>
      </div>

      {/* 3페이지: 부록 (문장 및 질문) */}
      <div className="pdf-page w-[210mm] h-[297mm] bg-[#FDFBF7] p-20 flex flex-col justify-center">
        <h3 className="text-2xl mb-8 font-serif text-slate-800">오래 간직할 문장</h3>
        {letterData.page_sentences?.map((sentence, idx) => (
          <p key={`s-${idx}`} className="mb-4 text-lg font-serif text-slate-600">"{sentence}"</p>
        ))}
        
        <h3 className="text-2xl mt-16 mb-8 font-serif text-slate-800">나에게 묻는 질문</h3>
        {letterData.page_questions?.map((q, idx) => (
          <p key={`q-${idx}`} className="mb-4 text-lg font-serif text-slate-600">Q. {q}</p>
        ))}

        {letterData.page_action && (
          <>
            <h3 className="text-2xl mt-16 mb-8 font-serif text-slate-800">오늘의 작은 행동</h3>
            <p className="text-lg font-serif text-slate-600">{letterData.page_action}</p>
          </>
        )}
      </div>
    </>
  )}
</div>
```

---

## 📝 작업 3: 다중 페이지 PDF 병합 다운로드 로직 적용
기존의 `html2canvas` 캡처 로직을 아래와 같이 **반복문을 도는 구조**로 교체하십시오.

```typescript
// 상단 import
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas-pro";

// handleDownloadPDF 함수 교체
const handleDownloadMultiPagePDF = async () => {
  setIsGeneratingPDF(true); // 버튼 스피너 표시용 State
  
  try {
    const pdf = new jsPDF("p", "mm", "a4");
    const pages = document.querySelectorAll('.pdf-page'); // 방금 만든 숨겨진 DOM들
    
    if (pages.length === 0) throw new Error("캡처할 페이지가 없습니다.");

    for (let i = 0; i < pages.length; i++) {
      const canvas = await html2canvas(pages[i] as HTMLElement, { 
        scale: 2, 
        useCORS: true 
      });
      
      const imgData = canvas.toDataURL('image/png');
      
      // 첫 페이지가 아니면 PDF에 새 페이지 추가
      if (i > 0) pdf.addPage();
      
      pdf.addImage(imgData, 'PNG', 0, 0, 210, 297);
    }
    
    pdf.save(`문장처방전_${new Date().getTime()}.pdf`);
  } catch (error) {
    console.error("다중 페이지 PDF 생성 에러:", error);
    alert("PDF 생성 중 오류가 발생했습니다.");
  } finally {
    setIsGeneratingPDF(false);
  }
};
```

---

## 📝 작업 4: 시너지 UI 구현 (친구 선물하기 & 치유형 배경)

### 4-1. 친구 선물하기 번들 UI 추가
`page.tsx` 상단의 `TIERS` 배열 가장 끝에 다음 요금제를 추가하고, `beta`에 있던 `popular: true` 속성을 이쪽으로 옮기세요.
```typescript
{ 
  id: "gift", 
  name: "Gift Package", 
  desc: "소중한 사람에게 위로를 선물하세요 (PDF 엽서 발급)", 
  priceText: "12,000원 ($9.99)", 
  priceVal: 12000, 
  usd: "9.99",
  popular: true 
}
```
그리고 사연을 적는 `textarea` 하단에 선물하기 전용 이름 입력창을 만드세요.
```tsx
{selectedProduct?.id === "gift" && (
  <div className="w-full mt-4 animate-fade-in">
    <input 
      type="text" 
      placeholder="선물 받을 분의 성함(또는 애칭)을 적어주세요." 
      className="block w-full rounded-xl border border-amber-200 bg-white/60 p-4 text-slate-800 shadow-inner sm:text-lg transition-colors placeholder:text-slate-400 font-serif outline-none focus:ring-2 focus:ring-amber-300"
    />
  </div>
)}
```

### 4-2. 치유형 배경화면 랜덤 주입
`generateLetter` 함수 내부 또는 배경화면을 지정하는 부분에 아래 치유형 키워드 로직을 삽입하세요.
```typescript
const healingKeywords = ["dusk", "fog", "calm+waterside", "vintage+window"];
const randomKeyword = healingKeywords[Math.floor(Math.random() * healingKeywords.length)];
setBgUrl(`https://source.unsplash.com/1600x900/?${randomKeyword}`);
```

> **Codex 님, 위 4가지 작업을 `global-letters/src/app/page.tsx`에 신속하게 반영해 주시기 바랍니다.**
