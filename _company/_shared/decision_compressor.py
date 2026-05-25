#!/usr/bin/env python3
# version: compressor_v1
"""RAG Memory Decision Compressor — Sweeps the decisions.md file, parses past
unstructured feedback and decision nodes, and leverages the local GPU AI engine
(or rule-based deterministic fallback) to compress, merge, and clean duplicates/conflicts,
keeping the SLM local context window extremely compact and responsive.
"""
import os, sys, time, json, re, subprocess

# Windows cp949 인코딩 충돌 방지 및 이모지 한글 입출력 보증
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
DECISIONS_MD = os.path.join(HERE, "decisions.md")

sys.path.append(HERE)

def parse_decisions_structure(filepath):
    """decisions.md 파일을 읽어 상단 뼈대 전략(격리 보존 영역)과 하단 동적 피드백 영역으로 나눕니다."""
    if not os.path.exists(filepath):
        return "", ""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # '## 최근 주요 의사결정 로그' 또는 최초 날짜 패턴 '## [' 을 기준으로 분할 시도
    # 만약 패턴이 없다면 용량을 고려해 임의의 줄 수(처음 20줄)를 뼈대로 잡음
    split_patterns = [
        r"## 최근 주요 의사결정 로그",
        r"## \[\d{4}-\d{2}-\d{2}\]"
    ]
    
    split_index = -1
    for pat in split_patterns:
        match = re.search(pat, content)
        if match:
            split_index = match.start()
            break
            
    if split_index != -1:
        skeleton = content[:split_index].strip()
        dynamic_logs = content[split_index:].strip()
    else:
        # 분할 기준이 모호한 경우 첫 18줄은 뼈대, 나머지는 동적 로그로 간주
        lines = content.splitlines()
        if len(lines) > 18:
            skeleton = "\n".join(lines[:18]).strip()
            dynamic_logs = "\n".join(lines[18:]).strip()
        else:
            skeleton = content.strip()
            dynamic_logs = ""
            
    return skeleton, dynamic_logs

def compress_by_local_ai(dynamic_logs):
    """llm_adapter를 활용하여 중복 및 모순 지침을 AI 기반으로 압축 요약합니다."""
    try:
        import llm_adapter
        
        system_instruction = (
            "너는 1인 기업 RAG 전역 메모리 압축기이다. 주어진 지침 목록 중에서 중복되거나, "
            "서로 모순되는 구형 지침들을 하나로 명확히 병합하여 정제된 마크다운 리스트 형태로 요약해야 한다. "
            "절대 부가적인 설명이나 사족을 달지 말고, 에이전트들이 즉시 수행할 수 있는 '의사결정 규범'으로 한글 불릿 리스트만 출력해라."
        )
        
        prompt = f"""
다음은 지난 기간 동안 축적된 사장님의 피드백과 자율 사이클 의사결정 지침들입니다.
중복되는 내용이나 충돌하는 모순 지침을 찾아 말끔하게 요약 병합하고,
불필요한 시간 기록 등은 지우고 15개 내외의 강력하고 명확한 규범 불릿 리스트로 압축하여 한글로 재구성해 주십시오:

[지침 목록]
{dynamic_logs}
"""
        # 로컬 AI 추론 수행 (timeout 10초 가드 탑재되어 있음)
        ai_response = llm_adapter.generate_text(prompt=prompt, system_instruction=system_instruction)
        
        # 만약 로컬 AI가 데몬 미기동으로 Fallback Mock 텍스트를 돌려줬다면,
        # 이 텍스트는 릴스 대본이나 IT 칼럼이므로, 압축에는 사용하지 않고 Fallback 룰셋으로 스위칭하기 위해 예외를 던집니다.
        if "대본" in ai_response or "에반젤리스트" in ai_response or "연봉 3배" in ai_response:
            raise ValueError("Ollama offline: Fallback mockup returned.")
            
        return ai_response.strip()
    except Exception as e:
        # AI 압축 실패 시, None을 리턴하여 룰셋 기반 다이어트로 진입하게 가이드
        return None

def compress_by_fallback_rules(dynamic_logs):
    """로컬 AI 미가동 오프라인 상황 시, 정규식과 중복 제거를 결합한 규칙 기반의 100% 무중단 다이어트를 실행합니다."""
    # 불릿 기호(-, *)로 시작하는 지침 라인들을 추출
    lines = dynamic_logs.splitlines()
    guidelines = []
    
    for line in lines:
        cleaned = line.strip()
        # 불릿 포인트 추출 (- 로 시작하는 것 위주)
        if cleaned.startswith("-") or cleaned.startswith("*"):
            # 불릿 제거 및 앞뒤 공백 제거
            g_text = re.sub(r"^[\-\*\s]+", "", cleaned).strip()
            if g_text and len(g_text) > 4:
                guidelines.append(g_text)
                
    # 순서를 유지하며 텍스트 기반 중복 제거
    unique_guidelines = []
    seen = set()
    for g in guidelines:
        # 단어 수준 정규화로 중복 거르기
        norm = re.sub(r"\s+", "", g)
        if norm not in seen:
            seen.add(norm)
            unique_guidelines.append(g)
            
    # 최신성 유지를 위해 가장 최근에 수집된(리스트 하단) 15개의 지침을 엄선
    # decisions.md 하단에 붙으므로 뒤쪽이 최신
    recent_guidelines = unique_guidelines[-15:]
    
    # 마크다운 리스트로 조립
    if not recent_guidelines:
        return "- 일시적인 마케팅 및 디자인 파이프라인의 자율 안정화 지침을 최우선 수호한다.\n- 오류 발생 시 로컬 가상 추론 모드로 즉각 전환하여 회복탄력성을 보증한다."
        
    result_lines = [f"- {g}" for g in recent_guidelines]
    return "\n".join(result_lines)

def run_diet_compression(force=False, threshold_kb=30):
    """decisions.md의 RAG 메모리 용량을 검사하여 지능형 다이어트 압축을 기동합니다."""
    if not os.path.exists(DECISIONS_MD):
        return {"status": "skipped", "message": "decisions.md 파일이 존재하지 않습니다."}

    orig_size = os.path.getsize(DECISIONS_MD)
    orig_size_kb = orig_size / 1024.0

    # 임계 용량(기본 30KB)을 넘지 않고 강제 기동 인자도 없다면 압축 생략
    if orig_size_kb < threshold_kb and not force:
        return {
            "status": "skipped",
            "message": f"현재 파일 크기({orig_size_kb:.2f}KB)가 임계값({threshold_kb}KB) 미만이므로 압축을 생략합니다."
        }

    print(f"📡 [RAG 메모리 다이어트] 파일 크기 {orig_size_kb:.2f}KB 스캔 완료. 압축 다이어트를 기동합니다...")

    skeleton, dynamic_logs = parse_decisions_structure(DECISIONS_MD)
    
    # 1. 로컬 AI 압축 시도
    method = "Local AI (GPU/SLM)"
    compressed_logs = compress_by_local_ai(dynamic_logs)
    
    # 2. 로컬 AI가 비활성화되었거나 비압축용 응답일 때, 오프라인 규칙 룰셋 다이어트 전환
    if not compressed_logs:
        method = "Deterministic Rule-based Fallback"
        compressed_logs = compress_by_fallback_rules(dynamic_logs)

    # 3. 새로운 decisions.md 파일 빌드
    new_date = time.strftime('%Y-%m-%d')
    new_content = f"""{skeleton}

## 최근 주요 의사결정 로그 ({method} 지능형 압축 적용)
*압축 갱신일: {new_date}*

{compressed_logs}
"""
    # 쓰기 작업 수행
    with open(DECISIONS_MD, "w", encoding="utf-8") as f:
        f.write(new_content.strip() + "\n")

    new_size = os.path.getsize(DECISIONS_MD)
    reduction_pct = (1.0 - (new_size / float(orig_size))) * 100.0 if orig_size > 0 else 0.0

    # 4. SQLite DB 감사 로그 연동 기록
    try:
        import database
        database.init_db()
        log_detail = (
            f"RAG Memory compressed using {method}. "
            f"Size: {orig_size_kb:.2f}KB -> {new_size/1024.0:.2f}KB ({reduction_pct:.1f}% reduction)"
        )
        database.log_audit("ceo", "COMPRESSION_RUN", log_detail)
    except Exception as e:
        print(f"⚠️ 압축 감사 로그 SQLite 연동 실패: {e}")

    return {
        "status": "success",
        "method": method,
        "original_size_kb": round(orig_size_kb, 2),
        "compressed_size_kb": round(new_size / 1024.0, 2),
        "reduction_percentage": round(reduction_pct, 1)
    }

def main():
    force_run = "--force" in sys.argv
    # 테스트 등 빠른 기동을 위해 CLI 실행 시 threshold를 기본 30KB로 잡되
    # 강제 실행 옵션이 있다면 즉시 구동시킵니다.
    res = run_diet_compression(force=force_run, threshold_kb=30)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
