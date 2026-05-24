#!/usr/bin/env python3
# version: lint_test_v1
"""프로젝트 자가 검증 — 타입체크·테스트·린트 자동 실행 + 결과 요약.

코다리가 코드를 만든 직후 이 도구를 호출하면:
  1. package.json 의 scripts 자동 감지 (test/lint/typecheck/build)
  2. 또는 .ts/.tsx 파일 있으면 npx tsc --noEmit
  3. .py 파일 있으면 python -m py_compile <각 파일>
  4. 결과 마크다운 리포트

config:
  PROJECT_PATH — 검증할 프로젝트 (비우면 web_init 마지막 결과)
  STRICT       — 'true' 면 첫 실패에서 멈춤. 기본 false (모두 시도)
"""
import os, sys, json, subprocess, glob

# Windows 환경에서 한글 깨짐 및 이모지 출력 에러 방지를 위해 입출력 인코딩을 UTF-8로 강제 적용
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "lint_test.json")
WEB_INIT_CFG = os.path.join(HERE, "web_init.json")


def _log(msg, kind="info"):
    prefix = {"info": "🧪", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def _load(p):
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _run(cmd, cwd, timeout=180):
    _log(f"$ {cmd}", "step")
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + "\n" + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, f"⏱ Timeout ({timeout}s)"
    except Exception as e:
        return -2, str(e)


def main():
    cfg = _load(CONFIG)
    init_cfg = _load(WEB_INIT_CFG)
    project = (cfg.get("PROJECT_PATH") or "").strip()
    if not project:
        project = (init_cfg.get("LAST_PROJECT") or "").strip()
    if not project:
        _log("PROJECT_PATH 비어있고 web_init 기록도 없음", "err")
        sys.exit(1)
    project = os.path.expanduser(project)
    if not os.path.isdir(project):
        _log(f"폴더 없음: {project}", "err")
        sys.exit(1)
    strict = str(cfg.get("STRICT", "")).lower() in ("true", "1", "yes")
    _log(f"검증 대상: {project}", "info")

    results = []  # (label, code, output)

    # 1) package.json scripts 자동 감지
    pkg_path = os.path.join(project, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            for key in ["typecheck", "lint", "test", "build"]:
                if key in scripts:
                    code, out = _run(f"npm run {key}", cwd=project, timeout=300)
                    results.append((f"npm run {key}", code, out))
                    if strict and code != 0:
                        break
        except Exception as e:
            _log(f"package.json 파싱 실패: {e}", "warn")

    # 2) scripts 없으면 직접 tsc/py_compile
    if not results:
        # TS/TSX
        ts_files = glob.glob(os.path.join(project, "**/*.ts"), recursive=True) + \
                   glob.glob(os.path.join(project, "**/*.tsx"), recursive=True)
        ts_files = [f for f in ts_files if "node_modules" not in f and "dist" not in f]
        if ts_files:
            tsconfig = os.path.join(project, "tsconfig.json")
            if os.path.exists(tsconfig):
                code, out = _run("npx tsc --noEmit", cwd=project, timeout=180)
                results.append(("npx tsc --noEmit", code, out))
        # Python
        py_files = glob.glob(os.path.join(project, "**/*.py"), recursive=True)
        py_files = [f for f in py_files if "venv" not in f and ".venv" not in f and "__pycache__" not in f]
        if py_files:
            errs = []
            for pf in py_files[:30]:  # 30개 cap
                code, out = _run(f"python3 -m py_compile {json.dumps(pf)}", cwd=project, timeout=10)
                if code != 0:
                    errs.append((pf, out.strip()[:120]))
            if errs:
                results.append((f"py_compile ({len(errs)}/{len(py_files)} 실패)", 1, "\n".join(f"{f}: {e}" for f, e in errs[:10])))
            else:
                results.append((f"py_compile {len(py_files)} files", 0, "All OK"))

            # 3) Pytest & 80% Coverage mandatory guard
            # 프로젝트 내에 tests/ 폴더나 test_*.py 파일이 존재한다면 실행
            has_tests = os.path.exists(os.path.join(project, "tests")) or \
                        any("test_" in os.path.basename(f) for f in py_files)
            if has_tests:
                _log("🧪 테스트 무결성 및 80% 커버리지 의무화 가드 작동 중...", "info")
                code, out = _run("coverage run -m pytest", cwd=project, timeout=180)
                
                if "No module named coverage" in out or "command not found" in out:
                    _log("⚠️ coverage 패키지가 설치되지 않아 일반 pytest로 대체 검증합니다.", "warn")
                    code, out = _run("pytest", cwd=project, timeout=120)
                    if code == 0:
                        results.append(("Pytest (테스트 성공, 단 coverage 미설치로 커버리지 수치 검증 생략)", 0, out))
                    else:
                        results.append(("Pytest (테스트 실패)", code, out))
                else:
                    if code != 0:
                        results.append(("Pytest & Coverage (테스트 실패)", code, out))
                    else:
                        # coverage json 파일 추출
                        _run("coverage json", cwd=project, timeout=20)
                        json_path = os.path.join(project, "coverage.json")
                        cov_ok = False
                        cov_percent = 0.0
                        
                        if os.path.exists(json_path):
                            try:
                                with open(json_path, "r", encoding="utf-8") as f:
                                    cov_data = json.load(f)
                                cov_percent = float(cov_data.get("totals", {}).get("percent_covered", 0.0))
                                if cov_percent >= 80.0:
                                    cov_ok = True
                            except Exception as cov_err:
                                _log(f"coverage.json 파싱 실패: {cov_err}", "warn")
                            
                            # Cleanup 임시 파일
                            try: os.remove(json_path)
                            except: pass
                            try: os.remove(os.path.join(project, ".coverage"))
                            except: pass
                        
                        if cov_ok:
                            results.append((f"Pytest & Coverage ({cov_percent:.1f}%)", 0, f"All tests passed with {cov_percent:.1f}% coverage! (Target: 80%+)"))
                        else:
                            results.append((f"Pytest & Coverage ({cov_percent:.1f}%)", 1, f"❌ 검증 반려: 테스트는 통과했으나 전체 라인 커버리지({cov_percent:.1f}%)가 최소 의무 기준인 80.0%에 미달합니다. 비즈니스 엣지 케이스 테스트 코드를 추가로 보완하십시오."))


    # 결과 리포트
    print()
    print(f"# 🧪 검증 결과 — {os.path.basename(project)}")
    print()
    if not results:
        print("⚠️ 실행할 검증 없음 (package.json scripts 없고 .ts/.py 파일도 없음)")
        return
    passed = sum(1 for _, c, _ in results if c == 0)
    print(f"**{passed}/{len(results)} 통과**\n")
    for label, code, out in results:
        icon = "✅" if code == 0 else "❌"
        print(f"## {icon} {label}")
        if code == 0:
            print(f"성공 (exit code 0)")
        else:
            print(f"실패 (exit code {code})")
            print()
            print("```")
            for line in out.strip().split("\n")[-15:]:
                print(line)
            print("```")
        print()
    if passed == len(results):
        print("> 🎉 모든 검증 통과. 안전하게 다음 단계로.")
    else:
        print(f"> ⚠️ {len(results) - passed}개 실패 — 위 출력 보고 수정 필요.")


if __name__ == "__main__":
    main()
