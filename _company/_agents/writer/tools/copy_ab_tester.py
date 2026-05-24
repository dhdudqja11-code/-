#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✍️ 마케팅 후크 자가 검증 및 가상 CTR 예측기 (copy_ab_tester.py)

카피라이터 에이전트가 만든 광고 카피나 마케팅 문구의 소구력을 평가하고,
심의 규정 위반 소지를 사전에 걸러 자가 치유를 도모합니다.
"""
import os
import sys
import json
import time
import io
import re
import argparse

# 윈도우 한글 콘솔 및 이모지 출력 시 cp949 인코딩 크래시 원천 방어
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_JSON = os.path.join(HERE, "copy_ab_tester.json")

def load_config():
    """copy_ab_tester.json 설정 로드"""
    default_cfg = {
        "MIN_PASS_CTR_PERCENT": 3.5,
        "DEFAULT_PERSONA": "SOLOPRENEUR",
        "PERSONAS": {
            "2030_OFFICE_WORKER": {
                "name": "2030 트렌디 직장인",
                "keywords": ["효율", "트렌드", "성장", "이지", "스마트", "루틴", "커리어", "꿀팁"],
                "base_ctr": 1.8
            },
            "4050_PARENT": {
                "name": "4050 알뜰 부모/주부",
                "keywords": ["가족", "안전", "건강", "알뜰", "할인", "신뢰", "정직", "혜택", "교육"],
                "base_ctr": 1.5
            },
            "SOLOPRENEUR": {
                "name": "1인 창업가 / 소상공인",
                "keywords": ["자동화", "시간 절약", "매출", "수익", "무료", "비결", "지름길", "성공"],
                "base_ctr": 2.2
            }
        },
        "PROHIBITED_WORDS": [
            r"100%.*?(확실|보장|성공|완벽)", 
            r"무조건.*?(성공|보장|확실|완벽)", 
            r"세계\s*(최초|유일|최고)", 
            r"우주\s*(유일|최고)", 
            r"가장\s*완벽", 
            r"부작용\s*(없음|제로)", 
            r"원금\s*보장", 
            r"인생\s*역전", 
            r"최고의\s*효능"
        ]
    }
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_cfg.update(cfg)
        except Exception as e:
            print(f"⚠️ [AB Tester] 설정을 읽는 중 오류 (기본값 사용): {e}", file=sys.stderr)
    return default_cfg

def analyze_copy(copy_text, persona_id=None):
    """카피 문구를 NLP적으로 분석하여 가상 CTR 및 심의 리스크 산출"""
    cfg = load_config()
    personas = cfg.get("PERSONAS", {})
    
    if not persona_id or persona_id not in personas:
        persona_id = cfg.get("DEFAULT_PERSONA", "SOLOPRENEUR")
        
    p_info = personas[persona_id]
    
    # 1. 베이스 클릭률 설정
    ctr = p_info.get("base_ctr", 2.0)
    
    # 2. NLP 가산점 분석
    modifications = []
    
    # (1) 숫자(정량성)의 존재 여부 체크
    has_number = bool(re.search(r'\d+', copy_text))
    if has_number:
        ctr += 0.8
        modifications.append("🔢 숫자의 구체성 활용 (+0.8%)")
        
    # (2) 의문문 또는 궁금증 유발 질문 후크 체크
    has_question = "?" in copy_text or "인가요" in copy_text or "방법은" in copy_text
    if has_question:
        ctr += 0.5
        modifications.append("❓ 질문 후크를 통한 궁금증 유발 (+0.5%)")
        
    # (3) 행동 촉구(CTA) 키워드 존재 여부 체크
    cta_words = ["지금", "바로", "확인", "신청", "무료로", "가이드", "비법"]
    has_cta = any(w in copy_text for w in cta_words)
    if has_cta:
        ctr += 0.6
        modifications.append("🎯 명확한 행동 촉구(CTA) 키워드 포함 (+0.6%)")
        
    # (4) 글자 수가 너무 길어 가독성이 저하되는지 체크
    if len(copy_text) > 80:
        ctr -= 0.6
        modifications.append("⚠️ 문장이 너무 길어 가독성 저하 (-0.6%)")
    elif len(copy_text) < 15:
        ctr -= 0.4
        modifications.append("⚠️ 카피가 너무 짧아 정보 전달력 부족 (-0.4%)")
        
    # (5) 타겟 페르소나 선호 키워드 일치 여부 체크
    matched_keywords = [w for w in p_info.get("keywords", []) if w in copy_text]
    if matched_keywords:
        bonus = min(len(matched_keywords) * 0.4, 1.2)
        ctr += bonus
        modifications.append(f"🔥 페르소나 선호 어휘 매칭 ({', '.join(matched_keywords)}) (+{bonus:.1f}%)")
        
    # 3. 과장광고 심의 규정 위반 검사 (Risk Check) - 정규식 패턴 분석 적용
    prohibited_list = cfg.get("PROHIBITED_WORDS", [])
    detected_violations = []
    for pattern in prohibited_list:
        if re.search(pattern, copy_text):
            # 매칭된 정규식 패턴을 사장님이 읽기 편한 이쁜 단어명으로 변환하여 등록
            clean_name = pattern.replace(r".*?", " ").replace(r"\s*", " ").replace(r"\s+", " ").replace("(", "").replace(")", "").replace("|", "/").replace("^", "").replace("$", "")
            detected_violations.append(clean_name)
    
    risk_score = len(detected_violations) * 35
    risk_level = "SAFE"
    if risk_score >= 70:
        risk_level = "HIGH_RISK"
    elif risk_score >= 35:
        risk_level = "WARNING"
        
    # 4. 종합 매력도 및 통과 등급 매기기
    min_pass = cfg.get("MIN_PASS_CTR_PERCENT", 3.5)
    
    # 리스크가 HIGH_RISK이면 강제 불합격 및 CTR 디스카운트 적용
    if risk_level == "HIGH_RISK":
        ctr = max(1.0, ctr - 2.0)
        is_pass = False
        reason = "❌ 심의 감점: 과장 광고 위반 단어가 2개 이상 검출되어 자가 가드독에 의해 반려되었습니다."
    elif ctr >= min_pass:
        is_pass = True
        reason = f"🎉 합격: 가상 CTR({ctr:.1f}%)이 최소 의무 기준인 {min_pass}%를 만족하여 통과했습니다."
    else:
        is_pass = False
        reason = f"❌ 반려: 가상 CTR({ctr:.1f}%)이 최소 기준치({min_pass}%)에 미달합니다. 문장 구조와 혜택 단어를 보강하십시오."
        
    # 5. 마크다운 보고서 생성
    report = f"""### ✍️ [카피 AB 테스트 & 가상 CTR 보고서]
* **검증 대상 페르소나**: `{p_info['name']}`
* **합격 가이드라인 CTR**: `최소 {min_pass}%`

#### 📊 NLP 소구점 분석
{chr(10).join(f"- {m}" for m in modifications) if modifications else "- 감지된 소구점 특징이 없음 (평이한 서술)"}

#### ⚠️ 광고 심의 리스크 검사
* **검출된 금지 어휘**: {f"`{', '.join(detected_violations)}`" if detected_violations else "특이사항 없음 (Safe)"}
* **위험 등급**: `{risk_level}` (위험 점수: {risk_score}/100)

#### 🏆 검증 최종 결과
* **예측 가상 CTR**: **{ctr:.1f}%**
* **판정 결과**: **{'✅ PASS' if is_pass else '❌ REJECT'}**
* **사유**: {reason}
"""
    
    return {
        "status": "ok" if is_pass else "rejected",
        "copy_text": copy_text,
        "persona": p_info['name'],
        "metrics": {
            "predicted_ctr": round(ctr, 2),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_pass": is_pass
        },
        "violations": detected_violations,
        "report_markdown": report
    }

def run_test():
    """자가 AB 테스트 모드"""
    print("🧪 [AB Tester] 마케팅 카피 자가 검증 및 CTR 연산 테스트 개시...\n")
    
    test_copies = [
        {
            "text": "세계 최초! 무조건 100% 성공을 보장하는 안티그래비티 배포 비결 대공개!",
            "label": "🔥 고위험/과대광고 카피 예제"
        },
        {
            "text": "1인 창업가를 위한 자동화 비법, 하루 2분 만에 세팅하는 3가지 무료 매뉴얼 확인하기!",
            "label": "✅ 저위험/고소구력 스마트 카피 예제"
        }
    ]
    
    success = True
    for t in test_copies:
        print(f"[{t['label']}]")
        print(f"\" {t['text']} \"")
        res = analyze_copy(t["text"])
        print(res["report_markdown"])
        print("-" * 50)
        
        # 테스트 검증용 로직
        if "고위험" in t["label"] and res["status"] != "rejected":
            success = False
        if "스마트" in t["label"] and res["status"] != "ok":
            success = False
            
    if success:
        print("🎉 [SUCCESS] 카피 AB 테스트 검증 및 심의 필터링이 100% 무결하게 정상 연산됨을 확인했습니다!")
    else:
        print("❌ [FAILURE] 예측 수치 또는 심의 리스크 필터 작동 오류 발생.", file=sys.stderr)
        
    return success

def main():
    parser = argparse.ArgumentParser(description="마케팅 후크 자가 검증 및 가상 CTR 예측 툴")
    parser.add_argument("--copy", type=str, help="검증할 마케팅 카피 문구")
    parser.add_argument("--persona", type=str, default=None, help="대상 페르소나 ID (2030_OFFICE_WORKER, 4050_PARENT, SOLOPRENEUR)")
    parser.add_argument("--test", action="store_true", help="스스로 마케팅 자가 검증 및 리포트 테스트 수행")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_test()
        sys.exit(0 if success else 1)
        
    if not args.copy:
        print("❌ 분석할 카피 문구가 입력되지 않았습니다. 사용법: copy_ab_tester.py --copy \"카피 내용\"")
        sys.exit(1)
        
    try:
        res = analyze_copy(args.copy, args.persona)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res["status"] == "ok" else 2)
    except Exception as e:
        print(f"❌ [AB Tester] 프로세스 실행 중 크래시: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
