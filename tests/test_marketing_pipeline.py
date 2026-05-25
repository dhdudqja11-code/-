# -*- coding: utf-8 -*-
import os
import json
import subprocess
import glob
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_marketing_trigger_endpoint():
    """
    POST /api/v1/marketing/trigger 호출 시 마케팅 승인 파일들이 정상 생성되는지 검증합니다.
    """
    # 1. 이전 승인 파일 청소
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(current_dir, ".."))
    pending_dir = os.path.join(workspace_dir, "_company", "approvals", "pending")
    
    if os.path.exists(pending_dir):
        for f in os.listdir(pending_dir):
            if f.startswith("apr-"):
                try:
                    os.unlink(os.path.join(pending_dir, f))
                except:
                    pass

    # 2. API 호출
    payload = {
        "task_id": "test-codari-game-101",
        "product_name": "초액션 우주 전사 게임",
        "product_description": "유니티 부럽지 않은 HTML5 초경량 스페이스 횡스크롤 슈팅 액션 게임"
    }
    
    response = client.post("/api/v1/marketing/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "apr-" in data["approval_id"]
    
    approval_id = data["approval_id"]
    
    # 3. 파일 물리적 생성 검증
    json_file = os.path.join(pending_dir, f"{approval_id}.json")
    md_file = os.path.join(pending_dir, f"{approval_id}.md")
    
    assert os.path.exists(json_file)
    assert os.path.exists(md_file)
    
    # 4. 콘텐츠 무결성 검증
    with open(json_file, "r", encoding="utf-8") as f:
        ap_data = json.load(f)
        
    assert ap_data["id"] == approval_id
    assert ap_data["kind"] == "marketing_release"
    assert ap_data["agentId"] == "marketing"
    assert ap_data["payload"]["product_name"] == "초액션 우주 전사 게임"
    assert "초액션 우주 전사 게임" in ap_data["payload"]["short_form"]
    assert "우주 전사" in ap_data["payload"]["long_form"]


def test_node_executor_execution():
    """
    Node.js 승인 집행자(Executor) 스크립트 기동 시 로컬 역사 파일 쓰기가 완벽하게 처리되는지 E2E로 검증합니다.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(current_dir, ".."))
    company_dir = os.path.join(workspace_dir, "_company")
    executor_path = os.path.join(company_dir, "approvals", "executors", "marketing_release.js")
    
    # 1. 마케팅 히스토리 폴더 청소
    history_base_dir = os.path.join(company_dir, "marketing_history")
    if os.path.exists(history_base_dir):
        # 기존 테스트 산출물 삭제
        import shutil
        try:
            shutil.rmtree(history_base_dir)
        except:
            pass
            
    # 2. 실행할 페이로드 데이터 빌드
    payload = {
        "task_id": "test-e2e-task-999",
        "product_name": "스마트 영양제 알리미 SaaS",
        "product_description": "사용자의 건강 상태 분석 후 최적의 영양제 섭취 타이밍을 텔레그램으로 알려주는 건강 알림 비서",
        "short_form": "💊 매일 까먹는 영양제, 이제 AI가 챙겨줍니다! '스마트 영양제 알리미 SaaS' 출시! 🚀",
        "long_form": "# 💊 건강 비서 영양제 알리미 출시\n\nAI가 추천하는 혁신적 영양제 솔루션!"
    }
    
    # 3. Node.js 프로세스 스폰 및 stdin 주입
    proc = subprocess.run(
        ["node", executor_path],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=company_dir
    )
    
    # 스크립트 성공 리턴(코드 0) 확인
    assert proc.returncode == 0
    print("Executor stdout:", proc.stdout)
    print("Executor stderr:", proc.stderr)
    
    # 4. 히스토리 폴더 및 텍스트 파일 생성 여부 완벽 검증
    assert os.path.exists(history_base_dir)
    
    # 생성된 릴리즈 폴더 찾기
    release_dirs = glob.glob(os.path.join(history_base_dir, "release_test-e2e-task-999_*"))
    assert len(release_dirs) == 1
    
    release_dir = release_dirs[0]
    short_file = os.path.join(release_dir, "short_form.txt")
    long_file = os.path.join(release_dir, "long_form_blog.md")
    
    assert os.path.exists(short_file)
    assert os.path.exists(long_file)
    
    # 컨텐츠 일치 확인
    with open(short_file, "r", encoding="utf-8") as f:
        assert "매일 까먹는 영양제" in f.read()
        
    with open(long_file, "r", encoding="utf-8") as f:
        assert "건강 비서 영양제 알리미 출시" in f.read()


def test_webhook_api_endpoint():
    """
    웹훅 엔드포인트의 데이터 수집이 올바르게 동작하고 수신 데이터가 저장되는지 테스트합니다.
    """
    # 1. 히스토리 초기화
    client.post("/api/v1/marketing/webhook/clear")
    
    # 2. 웹훅 전송 호출
    webhook_data = {
        "id": "release_test-codari-game-101",
        "kind": "marketing_release",
        "payload": {
            "task_id": "test-codari-game-101",
            "product_name": "초액션 우주 전사 게임",
            "short_form": "우주 전사 게임 고고!",
            "long_form": "# 우주 전사 게임 출시"
        },
        "approvedAt": "2026-05-25T13:30:00Z"
    }
    
    response = client.post("/api/v1/marketing/webhook", json=webhook_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # 3. 내역 조회 API를 통한 검증
    history_resp = client.get("/api/v1/marketing/webhook/history")
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert history_data["count"] == 1
    assert history_data["history"][0]["id"] == "release_test-codari-game-101"
