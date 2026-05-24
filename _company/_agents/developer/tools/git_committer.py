#!/usr/bin/env python3
import os
import sys
import io
import json
import subprocess
import argparse

# Windows cp949 인코딩으로 인한 이모지 출력 에러 방지 (강제 UTF-8 설정)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "git_committer.json")
WEB_INIT_CFG = os.path.join(HERE, "web_init.json")

def _log(msg, kind="info"):
    prefix = {"info": "⚙️", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)

def _load(p):
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def run_git(args, cwd):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def analyze_changes(diff_text, files_list, cfg):
    """diff 내용과 파일 목록을 분석하여 Conventional Commits 스타일의 메시지 유추"""
    types = cfg.get("conventional_types", ["feat", "fix", "docs", "style", "refactor", "test", "chore"])
    scope_mappings = cfg.get("scope_mappings", {})
    
    # 1. Scope 결정
    scope = "core"
    for path_pattern, mapped_scope in scope_mappings.items():
        if any(path_pattern in f for f in files_list):
            scope = mapped_scope
            break
            
    # 2. Type 결정 기본 로직
    commit_type = "refactor"
    
    # 파일 확장자 및 이름 분석
    has_test_files = any("test_" in os.path.basename(f) or ".test." in f for f in files_list)
    has_md_files = any(f.endswith(".md") for f in files_list)
    has_json_files = any(f.endswith(".json") for f in files_list)
    
    # diff 텍스트 특징 단어 분석
    diff_lc = diff_text.lower()
    
    if has_test_files:
        commit_type = "test"
    elif has_md_files and not any(f.endswith(".py") or f.endswith(".ts") or f.endswith(".js") for f in files_list):
        commit_type = "docs"
    elif has_json_files and not any(f.endswith(".py") or f.endswith(".ts") for f in files_list):
        commit_type = "config"
    elif "fix" in diff_lc or "bug" in diff_lc or "except" in diff_lc or "error" in diff_lc or "crash" in diff_lc:
        commit_type = "fix"
    elif "add" in diff_lc or "create" in diff_lc or "new" in diff_lc:
        commit_type = "feat"
    elif "refactor" in diff_lc or "clean" in diff_lc or "optimize" in diff_lc:
        commit_type = "refactor"
        
    # 3. 상세 요약 설명 작성
    summary = "update source files"
    if files_list:
        base_names = [os.path.basename(f) for f in files_list]
        if len(base_names) == 1:
            summary = f"modify {base_names[0]}"
            # diff를 보고 좀 더 상세하게 요약 가능
            lines = [l for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")]
            for line in lines:
                line_content = line[1:].strip()
                if "def " in line_content:
                    func_name = line_content.split("def ")[1].split("(")[0].strip()
                    summary = f"implement {func_name} function in {base_names[0]}"
                    break
                elif "class " in line_content:
                    class_name = line_content.split("class ")[1].split("(")[0].split(":")[0].strip()
                    summary = f"add {class_name} class to {base_names[0]}"
                    break
        elif len(base_names) <= 3:
            summary = f"update {', '.join(base_names)}"
        else:
            summary = f"update {len(base_names)} files including {base_names[0]}"
            
    # 글자수 제한 cap
    max_len = cfg.get("max_summary_length", 72)
    if len(summary) > max_len:
        summary = summary[:max_len-3] + "..."
        
    return f"{commit_type}({scope}): {summary}"

def main():
    parser = argparse.ArgumentParser(description="의미 기반 Conventional Commits 스마트 Git 커미터")
    parser.add_argument("--project", type=str, help="프로젝트 경로 (비워두면 web_init 자동 연동)")
    parser.add_argument("--message", type=str, help="커스터마이징된 커밋 요약 메시지 (수동 override용)")
    
    args = parser.parse_args()
    
    # 1. 프로젝트 경로 확인
    cfg = _load(CONFIG_PATH)
    init_cfg = _load(os.path.join(HERE, "web_init.json"))
    
    project = args.project or cfg.get("PROJECT_PATH") or init_cfg.get("LAST_PROJECT")
    if not project:
        _log("프로젝트 경로가 설정되지 않았습니다.", "err")
        sys.exit(1)
        
    project = os.path.expanduser(project)
    if not os.path.isdir(project):
        _log(f"유효한 폴더가 아닙니다: {project}", "err")
        sys.exit(1)
        
    _log(f"작업 대상 저장소: {project}", "info")
    
    # 2. git status --porcelain 스캔
    code, status_out, status_err = run_git(["status", "--porcelain"], cwd=project)
    if code != 0:
        _log(f"git status 실행 실패: {status_err}", "err")
        sys.exit(1)
        
    if not status_out:
        _log("커밋할 변경 사항이 존재하지 않습니다. (Clean Working Directory)", "warn")
        if not cfg.get("allow_empty_commit", False):
            sys.exit(0)
            
    # 3. 개별 파일 add (오염 차단)
    modified_files = []
    skipped_files = []
    
    for line in status_out.splitlines():
        if len(line) < 3:
            continue
        status_flag = line[:2]
        file_path = line[3:].strip()
        
        # 따옴표 제거 (파일명에 공백이 있어 인용 부호가 생기는 경우 대비)
        file_path = file_path.strip('"\'')
        
        # 오염 차단 필터링: 빌드/의존성/임시 파일 커밋 철저 방지
        block_keywords = [
            "node_modules/", "dist/", "build/", "out/", ".next/", 
            "package-lock.json", ".env", ".venv/", "venv/", 
            "__pycache__/", ".pytest_cache/", ".coverage", "coverage.json"
        ]
        if any(bk in file_path for bk in block_keywords):
            skipped_files.append(file_path)
            continue
            
        # 개별 git add 실행
        add_code, _, add_err = run_git(["add", file_path], cwd=project)
        if add_code == 0:
            modified_files.append(file_path)
        else:
            _log(f"파일 add 실패: {file_path} — {add_err}", "warn")
            
    if skipped_files:
        _log(f"불필요/임시 파일 {len(skipped_files)}개 커밋 대상에서 제외 완료 (안전 가드 작동)", "ok")
        
    if not modified_files:
        _log("커밋 대상 비즈니스 파일이 없습니다.", "warn")
        sys.exit(0)
        
    # 4. git diff --cached 획득 및 분석
    diff_code, diff_out, diff_err = run_git(["diff", "--cached"], cwd=project)
    if diff_code != 0:
        _log(f"git diff 획득 실패: {diff_err}", "err")
        sys.exit(1)
        
    # 5. 커밋 메시지 결정
    commit_msg = args.message
    if not commit_msg:
        commit_msg = analyze_changes(diff_out, modified_files, cfg)
        
    _log(f"자동 조율된 Conventional Commit 메시지:\n  ↳ \033[96m{commit_msg}\033[0m", "ok")
    
    # 6. git commit 실행
    commit_code, commit_out, commit_err = run_git(["commit", "-m", commit_msg], cwd=project)
    if commit_code == 0:
        print()
        print(f"## ✅ 스마트 커밋 성공: `{project.split('/')[-1]}`")
        print()
        print(f"- **커밋 메시지**: `{commit_msg}`")
        print(f"- **추가/수정된 파일 ({len(modified_files)}개)**:")
        for f in modified_files[:10]:
            print(f"  * `{f}`")
        if len(modified_files) > 10:
            print(f"  * 외 {len(modified_files)-10}개 더 있음...")
        print()
        _log("형상 관리가 안전하고 규칙적으로 업데이트되었습니다.", "ok")
    else:
        _log(f"git commit 실패: {commit_err}\n{commit_out}", "err")
        sys.exit(1)

if __name__ == "__main__":
    main()
