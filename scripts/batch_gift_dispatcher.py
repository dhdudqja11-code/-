#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎁 마음을 묻다 (Ask Your Heart) - 선물 예약 엽서 일괄 배치 전송 스크립트
작성자: Antigravity (풀스택 AI 에이전트)
목적: 매일 밤 자정 또는 스케줄링된 시간에 기동되어 Next.js /api/send-gift (GET) API를 안전하게 트리거하여
      대기 큐(gift_queue.json)에 적재된 모든 선물용 편지를 일괄 SMTP 전송(또는 샌드박스 시뮬레이션)합니다.
"""

import sys
import json
import urllib.request
import urllib.error
import time

# Prevent Windows cp949 UnicodeEncodeError when printing emojis/Korean in terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def dispatch_gift_batch():
    # 로컬 개발 포트 및 실 배포 주소 후보 리스트
    target_urls = [
        "http://localhost:3000/api/send-gift",
        "http://127.0.0.1:3000/api/send-gift"
    ]
    
    print("============================================================")
    print("🎁 [Gift Batch Dispatcher] 선물 엽서 일괄 전송 배치를 시작합니다.")
    print("============================================================")
    
    success = False
    error_logs = []
    
    for url in target_urls:
        try:
            print(f"🎯 트리거 타겟 URL 시도: {url}")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AskYourHeart-Batch-Dispatcher/1.0'}
            )
            
            # API GET 호출 (view=false 가 디폴트이므로 전송 트리거 작동)
            with urllib.request.urlopen(req, timeout=30) as response:
                res_body = response.read().decode('utf-8')
                res_data = json.loads(res_body)
                
                if res_data.get("success"):
                    print("============================================================")
                    print("🟢 [배치 전송 성공] 이메일 발송이 성공적으로 완수되었습니다!")
                    print(f"• 발송 건수: {res_data.get('count', 0)} / 전체 대기: {res_data.get('total', 0)}")
                    print(f"• 실행 모드: {res_data.get('mode', 'N/A')}")
                    print("============================================================")
                    success = True
                    break
                else:
                    print(f"⚠️ API 반환 에러: {res_data.get('error', 'Unknown Error')}")
                    error_logs.append(res_data.get('error'))
                    
        except urllib.error.URLError as e:
            err_msg = f"네트워크 통신 실패 (서버가 켜져 있는지 확인해 주세요): {e}"
            print(f"❌ {err_msg}")
            error_logs.append(err_msg)
        except Exception as e:
            err_msg = f"예기치 못한 시스템 에러: {e}"
            print(f"❌ {err_msg}")
            error_logs.append(err_msg)
        
        # 서버 기동 지연 대비 0.5초 대기
        time.sleep(0.5)

    if not success:
        print("\n============================================================")
        print("🔴 [배치 전송 실패] 모든 타겟 URL 호출에 실패했거나 에러가 발생했습니다.")
        print("• 에러 상세 요약:")
        for log in error_logs:
            print(f"  - {log}")
        print("============================================================")
        sys.exit(1)

if __name__ == "__main__":
    dispatch_gift_batch()
