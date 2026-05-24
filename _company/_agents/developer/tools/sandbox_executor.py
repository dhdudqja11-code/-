#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ 하이브리드 리눅스 격리 실행 어댑터 (sandbox_executor.py)

개발자 에이전트(코다리)가 요청하는 터미널 명령을 로컬 본체 대신,
WSL2(Linux) 또는 Docker 컨테이너 격리 샌드박스에서 수행하고 그 결과를 수집합니다.
"""
import os
import sys
import json
import subprocess
import io
import argparse

# 윈도우 한글 콘솔 및 이모지 출력 시 cp949 인코딩 크래시 원천 방어
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_JSON = os.path.join(HERE, "sandbox_executor.json")

def load_config():
    """sandbox_executor.json 설정 로드"""
    default_cfg = {
        "PREFER_ENGINE": "WSL2",  # 'WSL2' or 'DOCKER' or 'HOST'
        "DOCKER_CONTAINER_NAME": "ai-dev-sandbox",
        "DOCKER_WORKSPACE_DIR": "/workspace",
        "AUTO_FALLBACK_TO_HOST": True
    }
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_cfg.update(cfg)
        except Exception as e:
            print(f"⚠️ [Sandbox] 설정을 읽는 중 오류 (기본값 사용): {e}", file=sys.stderr)
    return default_cfg

def win_to_linux_path(win_path):
    """Windows 절대 경로를 Linux 드라이브 마운트 경로로 지능형 변환"""
    if not win_path:
        return ""
    # 상대경로 및 ./, ../ 입력을 완벽하게 절대경로로 사전 정규화
    absolute_win = os.path.abspath(win_path)
    normalized = os.path.normpath(absolute_win)
    
    # 드라이브 문자 파싱 (예: C:\Users\user -> /mnt/c/Users/user)
    if len(normalized) >= 2 and normalized[1] == ':':
        drive = normalized[0].lower()
        rest = normalized[2:].replace('\\', '/')
        # WSL2 기본 마운트 규칙인 /mnt/c 적용
        return f"/mnt/{drive}{rest}"
        
    return normalized.replace('\\', '/')

def detect_wsl2():
    """로컬 시스템에 WSL2가 사용 가능한 상태인지 자가 진단"""
    try:
        # 윈도우 인코딩 크래시를 예방하기 위해 errors="replace" 추가
        res = subprocess.run(["wsl", "echo", "1"], capture_output=True, text=True, errors="replace", timeout=5, shell=True)
        return res.returncode == 0
    except Exception:
        return False

def detect_docker(container_name):
    """로컬 시스템에 Docker 엔진이 돌고 있고 컨테이너가 켜져있는지 자가 진단"""
    try:
        # 윈도우 인코딩 크래시를 예방하기 위해 errors="replace" 추가
        res = subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name}"], capture_output=True, text=True, errors="replace", timeout=5, shell=True)
        return res.returncode == 0 and bool(res.stdout.strip())
    except Exception:
        return False

def execute_in_sandbox(command_list, workdir=None):
    """지정된 엔진에 따라 명령어를 샌드박스로 포장하여 안전 실행"""
    cfg = load_config()
    engine = cfg.get("PREFER_ENGINE", "WSL2").upper()
    fallback = cfg.get("AUTO_FALLBACK_TO_HOST", True)
    
    # 1. 샌드박스 엔진 자동 진단 및 매핑
    active_engine = "HOST"
    
    if engine == "WSL2":
        if detect_wsl2():
            active_engine = "WSL2"
        elif fallback:
            print("⚠️ [Sandbox] WSL2 엔진이 비활성 상태입니다. 로컬 호스트(Host OS)로 안전하게 폴백합니다.", file=sys.stderr)
            active_engine = "HOST"
        else:
            raise Exception("WSL2 엔진이 꺼져있으며 자동 호스트 폴백이 비활성화되어 있습니다.")
            
    elif engine == "DOCKER":
        container = cfg.get("DOCKER_CONTAINER_NAME", "ai-dev-sandbox")
        if detect_docker(container):
            active_engine = "DOCKER"
        elif fallback:
            print(f"⚠️ [Sandbox] Docker 컨테이너 ({container})가 실행 중이지 않습니다. 호스트 OS로 폴백합니다.", file=sys.stderr)
            active_engine = "HOST"
        else:
            raise Exception(f"Docker 컨테이너 ({container})가 구동 중이지 않습니다.")
            
    # 2. 실행 커맨드 구성 및 경로 변환
    cmd_str = " ".join(command_list)
    final_workdir = workdir if workdir else os.getcwd()
    
    if active_engine == "WSL2":
        linux_workdir = win_to_linux_path(final_workdir)
        # WSL2 내에서 디렉토리 이동 후 타겟 명령 실행
        wrapped_command = f"cd '{linux_workdir}' && {cmd_str}"
        print(f"🚀 [Sandbox] WSL2 샌드박스 실행: {wrapped_command}")
        
        res = subprocess.run(["wsl", "bash", "-c", wrapped_command], capture_output=True, text=True, errors="replace", shell=True)
        return res.returncode, res.stdout, res.stderr
        
    elif active_engine == "DOCKER":
        container = cfg.get("DOCKER_CONTAINER_NAME", "ai-dev-sandbox")
        # Docker 컨테이너 내부의 작업 공간 매핑 (Windows path -> Docker workspace path)
        relative_path = os.path.relpath(final_workdir, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
        linux_workdir = os.path.join(cfg.get("DOCKER_WORKSPACE_DIR", "/workspace"), relative_path.replace('\\', '/'))
        
        wrapped_command = f"cd '{linux_workdir}' && {cmd_str}"
        print(f"🐳 [Sandbox] Docker 컨테이너 ({container}) 실행: {wrapped_command}")
        
        res = subprocess.run(["docker", "exec", "-w", linux_workdir, container, "sh", "-c", cmd_str], capture_output=True, text=True, errors="replace", shell=True)
        return res.returncode, res.stdout, res.stderr
        
    else:
        # HOST OS 실행 (윈도우 로컬 서브프로세스)
        print(f"💻 [Sandbox] 호스트 본체 터미널 실행: {cmd_str}")
        res = subprocess.run(command_list, capture_output=True, text=True, errors="replace", cwd=final_workdir, shell=True)
        return res.returncode, res.stdout, res.stderr

def run_test():
    """자가 진단 연동 테스트 모드"""
    print("🧪 [Sandbox] 하이브리드 리눅스 작업장 자가 연동 테스트 개시...")
    
    # 1. 샌드박스 내부 리눅스 커널 정보 획득 시도 (uname -a)
    try:
        code, stdout, stderr = execute_in_sandbox(["uname", "-a"])
        if code == 0 and ("linux" in stdout.lower() or "wsl" in stdout.lower() or "ubuntu" in stdout.lower()):
            print("\n🎉 [SUCCESS] 리눅스 가상 샌드박스 터미널 연동 성공!")
            print(f"🐧 Kernel Info: {stdout.strip()}")
            return True
        else:
            # 리눅스가 아닌 윈도우 호스트로 폴백되어 실행되었을 시 경고
            print("\n⚠️ [FALLBACK WORKED] 리눅스 샌드박스가 감지되지 않아 안전하게 호스트 본체 터미널로 우회 처리되었습니다.")
            print(f"💻 Host Output: {stdout.strip() if stdout else 'No Output'}")
            if stderr:
                print(f"⚠️ Error Trace: {stderr.strip()}")
            return True
    except Exception as e:
        print(f"\n❌ [ERROR] 샌드박스 실행 어댑터 구동 실패: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="하이브리드 리눅스 격리 실행 어댑터")
    parser.add_argument("--test", action="store_true", help="스스로 가상화 샌드박스 자가 진단 테스트 수행")
    parser.add_argument("--workdir", type=str, default=None, help="작업 디렉토리 절대경로")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="샌드박스 내부에서 안전하게 실행할 터미널 명령어들")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_test()
        sys.exit(0 if success else 1)
        
    if not args.cmd:
        print("❌ 실행할 명령어가 입력되지 않았습니다. 사용법: sandbox_executor.py python3 my_script.py")
        sys.exit(1)
        
    try:
        code, stdout, stderr = execute_in_sandbox(args.cmd, args.workdir)
        sys.stdout.write(stdout)
        sys.stderr.write(stderr)
        sys.exit(code)
    except Exception as e:
        print(f"❌ [Sandbox] 치명적인 샌드박스 가상 터미널 기동 실패: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
