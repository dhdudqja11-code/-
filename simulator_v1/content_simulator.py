import os
import json
import random
from datetime import datetime

class ContentSimulator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()
        self.workspace_dir = os.path.dirname(os.path.dirname(config_path))
        
    def _load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def evaluate_content(self, scores):
        """
        scores: dict containing:
          - hooking_score
          - empathy_score
          - sales_connection
          - seo_score
          - cta_score
          - spam_risk
        returns: (decision, average_score, evaluation_report)
        """
        required_keys = ['hooking_score', 'empathy_score', 'sales_connection', 'seo_score', 'cta_score', 'spam_risk']
        for k in required_keys:
            if k not in scores:
                raise ValueError(f"Missing required evaluation score: {k}")
                
        # 수치 범위 검증 (0-100)
        for k in required_keys:
            val = scores[k]
            if not (0 <= val <= 100):
                raise ValueError(f"Score {k} must be between 0 and 100 (got {val})")

        average_score = sum(scores[k] for k in required_keys if k != 'spam_risk') / 5.0
        spam_risk = scores['spam_risk']

        # 추천 로직 처리 (upload_go, revision_needed, discard)
        # upload_go: 평균점수 >= 80 AND 스팸위험 < 30
        # discard: 평균점수 < 65 OR 스팸위험 >= 50
        # revision_needed: 그 외
        if average_score >= 80 and spam_risk < 30:
            decision = "upload_go"
        elif average_score < 65 or spam_risk >= 50:
            decision = "discard"
        else:
            decision = "revision_needed"

        report = {
            "evaluated_at": datetime.now().isoformat(),
            "scores": scores,
            "average_score": round(average_score, 2),
            "spam_risk": spam_risk,
            "decision": decision
        }
        return decision, average_score, report

    def run_revenue_simulation(self, decision, scores, baseline_traffic=None):
        """
        퍼널 추적 및 매출 모의실험 수행.
        decision이 'discard'인 경우 매출은 0으로 종결됩니다.
        """
        if decision == "discard":
            return {
                "status": "discarded",
                "total_predicted_revenue": 0,
                "funnel_summary": {}
            }

        # baseline_traffic이 제공되지 않은 경우 로컬 데이터에서 파싱 시도
        if baseline_traffic is None:
            baseline_traffic = self._get_baseline_traffic()

        # 시뮬레이션 활성화를 위해 최소 2000명의 Baseline Traffic 보장
        baseline_traffic = max(2000, baseline_traffic)

        # 채널 및 티어 요율 로드
        rev_config = self.config['revenue_simulation']
        channels = rev_config['channels']
        tiers = rev_config['tiers']

        # 콘텐츠 평가에 따른 보정치 (품질이 좋을수록 전환율이 상승)
        quality_multiplier = (scores['empathy_score'] * 0.4 + scores['cta_score'] * 0.4 + scores['sales_connection'] * 0.2) / 100.0
        
        # Revision Needed인 경우 노출수와 전환율에 패널티 부여 (보완이 필요하므로)
        revision_penalty = 0.6 if decision == "revision_needed" else 1.0

        simulation_results = {}
        total_predicted_revenue = 0
        total_purchases_by_tier = {tier: 0 for tier in tiers}

        # 각 채널별로 유입 시뮬레이션
        for channel_name, channel_info in channels.items():
            # 1. content_exposure (실제 방문자 대비 소셜 미디어 노출 배율 1000배 적용하여 모수 절삭 방지)
            base_exposure = baseline_traffic * 1000.0 * random.uniform(8.0, 12.0) * revision_penalty
            if channel_name == "instagram":
                exposure = base_exposure * 1.5
            elif channel_name == "blog":
                exposure = base_exposure * 1.2
            elif channel_name == "thread":
                exposure = base_exposure * 0.8
            else: # email
                exposure = base_exposure * 0.3

            # 채널 CTR (empathy, cta 점수 보정 적용)
            ctr_level = "mid"
            if scores['hooking_score'] >= 85:
                ctr_level = "high"
            elif scores['hooking_score'] < 65:
                ctr_level = "low"
            
            ctr = channel_info['ctr'][ctr_level] * quality_multiplier

            # 10단계 퍼널 트래킹 시뮬레이션 (float 유지하여 소수점 절삭 방지)
            # 2. stop_and_read
            stop_and_read = exposure * ctr
            
            # 3. save (저장수)
            save_rate = 0.15 * (scores['empathy_score'] / 100.0) * random.uniform(0.9, 1.1)
            save = stop_and_read * save_rate

            # 4. comment (댓글수)
            comment_rate = 0.05 * (scores['empathy_score'] / 100.0) * random.uniform(0.8, 1.2)
            comment = stop_and_read * comment_rate

            # 5. profile_visit (프로필 방문)
            profile_visit = (save + comment) * 0.4 * random.uniform(0.9, 1.1)

            # 6. link_click (링크 클릭)
            link_click_rate = 0.25 * (scores['cta_score'] / 100.0) * random.uniform(0.9, 1.1)
            link_click = profile_visit * link_click_rate

            # 7. detail_page_visit (상세페이지 방문)
            detail_page_visit = link_click * 0.8 * random.uniform(0.95, 1.05)

            # 각 상품 티어별 결제 시도 및 구매 완료 시뮬레이션
            tier_details = {}
            channel_revenue = 0

            for tier_name, tier_info in tiers.items():
                price = tier_info['price']
                if price == 0:
                    continue # Free 티어는 매출에서 제외
                
                # 티어 전환율 결정
                conv_level = "mid"
                if scores['sales_connection'] >= 85:
                    conv_level = "high"
                elif scores['sales_connection'] < 65:
                    conv_level = "low"

                conv_rate = tier_info['conversion_rates'][conv_level] * quality_multiplier * revision_penalty
                
                # 8. payment_attempt (결제 시도)
                payment_attempt = detail_page_visit * conv_rate * 1.2 * random.uniform(0.85, 1.15)
                
                # 9. purchase (구매 완료)
                purchase_rate = 0.9 * (scores['sales_connection'] / 100.0) * random.uniform(0.9, 1.1)
                purchase = payment_attempt * purchase_rate

                # 10. review (리뷰 작성)
                review = purchase * 0.15 * random.uniform(0.8, 1.2)

                # 최종 구매 정수화 (최소 0 이상)
                final_purchase = int(round(purchase))
                final_review = int(round(review))
                final_payment_attempt = int(round(payment_attempt))

                revenue = final_purchase * price
                channel_revenue += revenue
                total_predicted_revenue += revenue
                total_purchases_by_tier[tier_name] += final_purchase

                tier_details[tier_name] = {
                    "conversion_rate_used": round(conv_rate, 5),
                    "payment_attempt": final_payment_attempt,
                    "purchase": final_purchase,
                    "review": final_review,
                    "revenue": revenue
                }

            simulation_results[channel_name] = {
                "funnel": {
                    "content_exposure": int(round(exposure)),
                    "stop_and_read": int(round(stop_and_read)),
                    "save": int(round(save)),
                    "comment": int(round(comment)),
                    "profile_visit": int(round(profile_visit)),
                    "link_click": int(round(link_click)),
                    "detail_page_visit": int(round(detail_page_visit))
                },
                "tier_details": tier_details,
                "channel_revenue": channel_revenue
            }

        return {
            "status": "success",
            "decision": decision,
            "quality_multiplier": round(quality_multiplier, 4),
            "total_predicted_revenue": total_predicted_revenue,
            "total_purchases_by_tier": total_purchases_by_tier,
            "channels": simulation_results
        }

    def _get_baseline_traffic(self):
        """
        로컬 traffic_log.json에서 최근 접속 데이터를 읽어 기본 모수로 사용
        """
        traffic_log_path = os.path.join(self.workspace_dir, 'traffic_log.json')
        if os.path.exists(traffic_log_path):
            try:
                with open(traffic_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        # 가장 최근의 트래픽을 가져옴
                        latest_date = max(data.keys())
                        return max(10, data[latest_date]) # 최소 10명 보장
            except Exception:
                pass
        return 100 # 기본 폴백 값
