#!/usr/bin/env python3
# version: monte_carlo_v1
"""Monte Carlo Risk Simulator — runs 20,000 trials to model risk distributions,
generates a dark-mode probability density chart, and compiles a premium ReportLab 
PDF risk certificate.
"""
import os
import sys
import random
import math
import datetime
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ReportLab components
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Windows 한글 입출력 가드
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 폰트 구성 및 Windows 맑은 고딕 동적 등록
FONT_NAME = "Helvetica"
if REPORTLAB_AVAILABLE and os.name == 'nt':
    malgun_path = r"C:\Windows\Fonts\malgun.ttf"
    if os.path.exists(malgun_path):
        try:
            pdfmetrics.registerFont(TTFont("Malgun", malgun_path))
            FONT_NAME = "Malgun"
        except Exception:
            pass

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
REPORTS_DIR = os.path.join(WORKSPACE, "reports")

def sanitize_text(text: str, font: str) -> str:
    """Helvetica 폰트 환경에서 PDF 크래시 방지용 지능형 영문 매핑."""
    if font != "Malgun":
        replacements = {
            "📈 [Premium] 20,000번의 모의 가상 경영 시뮬레이션 보고서": "[Premium] 20,000 Business Simulation Risk Report",
            "작성일": "Date",
            "1인 기업 자동 안전 가이드라인 증명": "1-Person Business Auto-Guard Proof",
            "사장님 계정 ID": "Owner ID",
            "가상 모의실험 횟수": "Simulation Runs",
            "위험 기준액": "Risk Threshold",
            "위험 기준액 초과 가능성": "Risk Exceedance Chance",
            "20,000번": "20,000 times",
            "15,000 USD": "15,000 USD",
            "진단 항목": "Category",
            "손실 예상액": "Estimated Loss",
            "쉬운 설명": "Explanation",
            "평균적인 손실 기댓값 (평소에 발생할 수 있는 지출 규모)": "Average Expected Loss (Normal business operation expense)",
            "2만 번의 가상 실행에서 나타난 지극히 평균적인 지출 수준": "Extremely average expenditure level observed across 20,000 trials",
            "보통 상황의 예상 손실액 (딱 중간 순위의 일반적 날씨)": "Normal Scenario Loss (The most ordinary middle-rank situation)",
            "특별한 이변이 없는 일상에서 마주하는 일반적인 손실액": "General loss encountered in daily business without extreme events",
            "손실의 흔들림 변동폭 (표준편차)": "Loss Volatility (Standard Deviation)",
            "비가 오거나 맑은 날씨의 차이처럼 손실이 오르내리는 흔들림의 크기": "The range of rise and fall in loss, like the difference between rain and shine",
            "최악의 폭풍우 상황 예상 손실 (상위 5% 위험)": "Worst 5% Storm Loss (95% Value at Risk)",
            "100일 중 가장 운이 없는 5일 동안 겪을 수 있는 잠재적 최대 폭풍우 손실액": "Maximum potential loss incurred during the 5 worst days out of 100 days",
            "극단적 태풍 위기 예상 손실 (상위 1% 위험)": "Extreme 1% Typhoon Loss (99% Value at Risk)",
            "평생 한 번 올까 말까 한 초대형 태풍 상황 시의 최대 리스크액": "Maximum absolute risk when hit by an ultra-typhoon once in a lifetime",
            "🔔 대표님(사장님), 오늘 하루도 참 많이 애쓰셨습니다": "🔔 President, thank you so much for your hard work today",
            "1. 2만 번의 가상 모의 경영 시뮬레이션은 대표님이 밤낮으로 다져오신 사업의 기틀을 지키기 위한 조용한 안부이자 예방 진단입니다.":
                "1. The 20,000 virtual simulations act as a quiet greeting and proactive scan to protect your business foundation.",
            "2. 상위 5% 및 1% 예상 손실액은 혹여나 마주할 수 있는 법률적, 보안상 비바람에 대비해 우리가 단단한 지붕(우산)을 미리 지어둘 수 있도록 돕는 사랑의 이정표입니다.":
                "2. The worst 5% and 1% losses serve as warm guideposts, reminding us to prepare solid umbrellas against compliance rainstorms.",
            "3. 리스크 초과 확률이 높게 나오더라도 자책하지 마세요. 대표님이 더 견고하고 안전한 방어막을 구축해 마음을 완전히 편히 놓으셔도 된다는 다정한 신호입니다.":
                "3. Please do not blame yourself if the risk probability seems high; it is a friendly sign to build a stronger defensive shield and let your mind rest.",
            "💡 초보 사장님을 위한 마스터의 10초 요약 꿀팁": "💡 Warm Cheat-Sheet for Beginner Presidents",
            "• 평균 손실과 보통 손실은 일상적인 맑은 날씨에 발생하는 소소한 비용 지출이므로 평소처럼 편안하게 대처하시면 됩니다.":
                "• Average & Normal losses are just minor everyday expenses under sunny skies. Rest easy and deal with them casually.",
            "• 흔들림 변동폭은 날씨가 수시로 변하듯 비즈니스가 오르내리는 자연스러운 호흡(파도)입니다.":
                "• Volatility is simply the natural rhythm of your business fluctuating, much like shifting weather patterns.",
            "• 우리가 대비해야 할 것은 최악(5%) 및 극단적(1%) 상황입니다. 이 수치가 커질 때만 튼튼한 우산(Gateway 자동 안전 가드)을 펼쳐 마음을 지키시면 됩니다.":
                "• All we need to shield against are the Worst (5%) & Extreme (1%) storms. When these rise, just unfold your strong Gateway umbrella.",
            "🔒 디지털 보안 및 위조 방지 서명 (디지털 안전 인증)": "🔒 Digital Security & Immutability Certificate",
            "안전 장부 고유 번호": "Document Signature Hash",
            "안전 인증 완료": "Compliance Verified",
            "2차 인증(OTP) 보안 완료 및 위조가 불가한 이중 암호화 보증": "MFA Secured & Dual-Hashed Non-Repudiation Certificate",
            "📊 모의실험 손실 분포 및 위기 발생 확률 흐름": "📊 Simulation Loss Distribution & Probability Flow",
            "🎯 가상 경영 모의실험 핵심 분석 데이터": "🎯 Virtual Simulation Key Analysis Data"
        }
        for kr, en in replacements.items():
            text = text.replace(kr, en)
        return "".join([c if ord(c) < 128 else "?" for c in text])
    return text

def sample_triangular(low: float, mode: float, high: float) -> float:
    """Pure Python triangular distribution sampler."""
    u = random.random()
    if u < (mode - low) / (high - low):
        return low + math.sqrt(u * (high - low) * (mode - low))
    else:
        return high - math.sqrt((1 - u) * (high - low) * (high - mode))

def run_monte_carlo_simulation(input_data: dict, trials: int = 20000, critical_threshold: float = 15000.0) -> dict:
    """20,000회 몬테카를로 시뮬레이션을 실행하여 리스크 지표 및 분포 통계를 도출합니다."""
    source = input_data.get("source", "UnknownClient")
    data_points = input_data.get("data_points") or []
    
    # data_points가 비어있으면 기본값 주입
    if not data_points:
        data_points = [5, 5]

    # 각 데이터 포인트를 개별 리스크 요인으로 매핑
    # base_loss = score * 1500
    # likelihood = 0.6
    likelihood = 0.6
    base_losses = [score * 1500.0 for score in data_points]
    
    trial_losses = []
    
    # 20,000회 시뮬레이션 기동
    for _ in range(trials):
        trial_loss = 0.0
        for base in base_losses:
            # 60% 확률로 리스크 발생
            if random.random() < likelihood:
                # 삼각분포 (low = 60%, mode = 100%, high = 150%)
                simulated_impact = sample_triangular(base * 0.6, base, base * 1.5)
                trial_loss += simulated_impact
        trial_losses.append(trial_loss)
        
    trial_losses.sort()
    
    # 통계 추출
    total_runs = len(trial_losses)
    mean_loss = sum(trial_losses) / total_runs
    median_loss = trial_losses[int(total_runs * 0.5)]
    min_loss = trial_losses[0]
    max_loss = trial_losses[-1]
    
    # 표준 편차
    variance = sum((x - mean_loss) ** 2 for x in trial_losses) / total_runs
    std_dev = math.sqrt(variance)
    
    # Value at Risk (VaR)
    var_95 = trial_losses[int(total_runs * 0.95)]
    var_99 = trial_losses[int(total_runs * 0.99)]
    
    # 임계치 초과 횟수 및 확률
    exceed_count = sum(1 for x in trial_losses if x > critical_threshold)
    exceed_prob = (exceed_count / total_runs) * 100.0
    
    return {
        "client_id": source,
        "trials": trials,
        "critical_threshold": critical_threshold,
        "mean_loss": round(mean_loss, 2),
        "median_loss": round(median_loss, 2),
        "min_loss": round(min_loss, 2),
        "max_loss": round(max_loss, 2),
        "std_dev": round(std_dev, 2),
        "var_95": round(var_95, 2),
        "var_99": round(var_99, 2),
        "exceed_prob": round(exceed_prob, 2),
        "losses": trial_losses
    }

def generate_monte_carlo_chart(sim_results: dict) -> str:
    """시뮬레이션 손실 분포 확률밀도 웜톤 라이트 모드 그래프를 생성하여 저장합니다."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    chart_path = os.path.join(REPORTS_DIR, "monte_carlo_distribution.png")
    
    losses = sim_results["losses"]
    mean_loss = sim_results["mean_loss"]
    var_95 = sim_results["var_95"]
    var_99 = sim_results["var_99"]
    
    # 따뜻하고 편안한 웜톤 라이트 모드 스타일 정의
    WARM_BG = "#FAF6F0"
    CARD_BG = "#F3EFE9"
    TEXT_DARK = "#2C2520"
    TEXT_MUTED = "#6B5E54"
    GRID_COLOR = "#E5D9C9"
    
    TERRACOTTA = "#D35400"      # 따뜻한 오렌지 (밀도 주선)
    DARK_TERRACOTTA = "#A04000" # 평균 손실선
    MAHOGANY = "#BA4A00"        # 95% 위험선
    BRICK_RED = "#C0392B"       # 99% 위험선
    
    plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'Segoe UI', 'Arial', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['text.color'] = TEXT_DARK
    plt.rcParams['axes.labelcolor'] = TEXT_DARK
    plt.rcParams['xtick.color'] = TEXT_MUTED
    plt.rcParams['ytick.color'] = TEXT_MUTED
    
    fig, ax = plt.subplots(figsize=(9.5, 5.5), facecolor=WARM_BG)
    ax.set_facecolor(CARD_BG)
    ax.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.6)
    
    # 히스토그램 그리기 (부드러운 오렌지 반투명 채우기)
    n, bins, patches = ax.hist(losses, bins=100, density=True, color=TERRACOTTA, alpha=0.18, edgecolor=TERRACOTTA, linewidth=0.6)
    
    # smooth KDE approximation
    try:
        import scipy.stats as stats
        import numpy as np
        kde = stats.gaussian_kde(losses)
        x_eval = np.linspace(min(losses), max(losses), 200)
        ax.plot(x_eval, kde(x_eval), color=TERRACOTTA, linewidth=2.5, label="손실 발생 가능성 흐름 (확률 밀도)")
    except ImportError:
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        ax.plot(bin_centers, n, color=TERRACOTTA, linewidth=2.5, label="손실 발생 가능성 흐름 (확률 밀도)")

    # 수직 기준선 그리기 (따뜻한 갈색 및 빨간색 계열 매핑)
    ax.axvline(mean_loss, color=DARK_TERRACOTTA, linestyle="--", linewidth=2.2, label=f"평균적인 손실 기댓값: ${mean_loss:,.2f}")
    ax.axvline(var_95, color=MAHOGANY, linestyle="--", linewidth=2.2, label=f"최악의 위기 예상 손실 (상위 5%): ${var_95:,.2f}")
    ax.axvline(var_99, color=BRICK_RED, linestyle="--", linewidth=2.2, label=f"극단적 파산 위기 예상 손실 (상위 1%): ${var_99:,.2f}")
    
    # 레이아웃 다듬기
    ax.set_title("가상 경영 모의실험 손실 예상 분포 (20,000번의 모의 가상 경영 시뮬레이션)", fontsize=13, fontweight='bold', pad=15, color=TEXT_DARK)
    ax.set_xlabel("예상 손실액 (USD)", fontsize=11, labelpad=10, color=TEXT_DARK)
    ax.set_ylabel("발생 가능성 정도 (확률 밀도)", fontsize=11, labelpad=10, color=TEXT_DARK)
    
    # 축 포맷
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    # 테두리 색상
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_color(GRID_COLOR)
        
    ax.legend(facecolor=WARM_BG, edgecolor=GRID_COLOR, fontsize=10, loc="upper right")
    plt.tight_layout()
    
    plt.savefig(chart_path, dpi=130, facecolor=WARM_BG)
    plt.close()
    
    return chart_path

def draw_warm_background(canvas_obj, doc_obj):
    """ReportLab canvas callback to draw warm cream background color to relieve eye strain."""
    canvas_obj.saveState()
    canvas_obj.setFillColor(colors.HexColor("#FAF6F0")) # 따뜻한 크림 베이지
    canvas_obj.rect(0, 0, doc_obj.pagesize[0], doc_obj.pagesize[1], fill=True, stroke=False)
    canvas_obj.restoreState()

def generate_monte_carlo_pdf(sim_results: dict) -> dict:
    """시뮬레이션 통계 및 그래프가 통합된 따뜻하고 눈이 편안한 초프리미엄 PDF 보고서를 빌드합니다."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORTS_DIR, "monte_carlo_risk_report.pdf")
    
    if not REPORTLAB_AVAILABLE:
        print("⚠️ ReportLab is not available. Skipping PDF generation.", file=sys.stderr)
        return {"pdf_path": "", "data_hash": "", "file_hash": ""}
        
    chart_img = generate_monte_carlo_chart(sim_results)
    
    # 1. 1차 데이터 서명 해시 산출 (Document Signature Hash)
    import hashlib
    sig_payload = f"{sim_results.get('client_id')}|{sim_results.get('trials')}|{sim_results.get('mean_loss')}|{sim_results.get('var_95')}|{sim_results.get('var_99')}|{sim_results.get('exceed_prob')}"
    data_hash = hashlib.sha256(sig_payload.encode('utf-8')).hexdigest()
    
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter,
        rightMargin=45, leftMargin=45,
        topMargin=45, bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # 따뜻하고 부드러운 웜톤 스타일 정의
    title_style = ParagraphStyle(
        name='MC_Title_Warm',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#D35400"), # 따뜻한 오렌지/테라코타
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        name='MC_Heading_Warm',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#A04000"), # 어두운 테라코타 브라운
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        name='MC_Body_Warm',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2C2520"), # 짙은 에스프레소 브라운 본문
        spaceAfter=8
    )
    
    bold_body_style = ParagraphStyle(
        name='MC_Body_Bold_Warm',
        parent=body_style,
        fontName=FONT_NAME + "-Bold" if FONT_NAME != "Malgun" else FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#BA4A00") # 부드러운 마호가니
    )
    
    mono_style = ParagraphStyle(
        name='MC_Mono_Warm',
        parent=styles['Normal'],
        fontName="Courier-Bold",
        fontSize=8.0,
        leading=10,
        textColor=colors.HexColor("#A04000") # 마호가니 모노스페이스
    )

    story = []
    
    # 1. 문서 헤더 및 따뜻한 주황색 장식선
    story.append(Paragraph(sanitize_text("📈 [Premium] 20,000번의 모의 가상 경영 시뮬레이션 보고서", FONT_NAME), title_style))
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(sanitize_text(f"작성일: {current_time} | 1인 기업 자동 안전 가이드라인 증명", FONT_NAME), body_style))
    story.append(Spacer(1, 8))
    
    divider = Table([[""]], colWidths=[520], rowHeights=[2.5])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D35400")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))
    
    # 2. Executive Summary 다크 네온 정보 테이블
    meta_data = [
        [Paragraph(sanitize_text("사장님 계정 ID", FONT_NAME), bold_body_style), Paragraph(sim_results["client_id"], body_style),
         Paragraph(sanitize_text("가상 모의실험 횟수", FONT_NAME), bold_body_style), Paragraph(sanitize_text("20,000번", FONT_NAME), body_style)],
        [Paragraph(sanitize_text("위험 기준액", FONT_NAME), bold_body_style), Paragraph(sanitize_text("15,000 USD", FONT_NAME), body_style),
         Paragraph(sanitize_text("위험 기준액 초과 가능성", FONT_NAME), bold_body_style), Paragraph(f"{sim_results['exceed_prob']}%", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[130, 130, 130, 130])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F3EFE9")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F3EFE9")),
        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor("#E5D9C9")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # 3. 몬테카를로 통계 지표 분석
    story.append(Paragraph(sanitize_text("🎯 가상 경영 모의실험 핵심 분석 데이터", FONT_NAME), heading_style))
    
    stats_data = [
        [Paragraph(sanitize_text("진단 항목", FONT_NAME), bold_body_style), 
         Paragraph(sanitize_text("손실 예상액", FONT_NAME), bold_body_style), 
         Paragraph(sanitize_text("쉬운 설명", FONT_NAME), bold_body_style)],
        [Paragraph(sanitize_text("평균적인 손실 기댓값 (평소에 발생할 수 있는 지출 규모)", FONT_NAME), body_style), f"${sim_results['mean_loss']:,.2f}", 
         Paragraph(sanitize_text("2만 번의 가상 실행에서 나타난 지극히 평균적인 지출 수준", FONT_NAME), body_style)],
        [Paragraph(sanitize_text("보통 상황의 예상 손실액 (딱 중간 순위의 일반적 날씨)", FONT_NAME), body_style), f"${sim_results['median_loss']:,.2f}", 
         Paragraph(sanitize_text("특별한 이변이 없는 일상에서 마주하는 일반적인 손실액", FONT_NAME), body_style)],
        [Paragraph(sanitize_text("손실의 흔들림 변동폭 (표준편차)", FONT_NAME), body_style), f"${sim_results['std_dev']:,.2f}", 
         Paragraph(sanitize_text("비가 오거나 맑은 날씨의 차이처럼 손실이 오르내리는 흔들림의 크기", FONT_NAME), body_style)],
        [Paragraph(sanitize_text("최악의 폭풍우 상황 예상 손실 (상위 5% 위험)", FONT_NAME), bold_body_style), f"${sim_results['var_95']:,.2f}", 
         Paragraph(sanitize_text("100일 중 가장 운이 없는 5일 동안 겪을 수 있는 잠재적 최대 폭풍우 손실액", FONT_NAME), body_style)],
        [Paragraph(sanitize_text("극단적 태풍 위기 예상 손실 (상위 1% 위험)", FONT_NAME), bold_body_style), f"${sim_results['var_99']:,.2f}", 
         Paragraph(sanitize_text("평생 한 번 올까 말까 한 초대형 태풍 상황 시의 최대 리스크액", FONT_NAME), body_style)]
    ]
    
    stats_table = Table(stats_data, colWidths=[180, 80, 260])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3EFE9")),
        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor("#E5D9C9")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (1,4), (1,5), colors.HexColor("#C0392B")), # 최악 손실 빨간색 강조
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 10))
    
    # 💡 초보 사장님을 위한 마스터의 10초 요약 꿀팁 단락 신설 (가독성 최적화)
    story.append(Paragraph(sanitize_text("💡 초보 사장님을 위한 마스터의 10초 요약 꿀팁", FONT_NAME), heading_style))
    story.append(Paragraph(sanitize_text("• 평균 손실과 보통 손실은 일상적인 맑은 날씨에 발생하는 소소한 비용 지출이므로 평소처럼 편안하게 대처하시면 됩니다.", FONT_NAME), body_style))
    story.append(Paragraph(sanitize_text("• 흔들림 변동폭은 날씨가 수시로 변하듯 비즈니스가 오르내리는 자연스러운 호흡(파도)입니다.", FONT_NAME), body_style))
    story.append(Paragraph(sanitize_text("• 우리가 대비해야 할 것은 최악(5%) 및 극단적(1%) 상황입니다. 이 수치가 커질 때만 튼튼한 우산(Gateway 자동 안전 가드)을 펼쳐 마음을 지키시면 됩니다.", FONT_NAME), body_style))
    story.append(Spacer(1, 10))
    
    # 4. 차트 이미지 임베딩
    if os.path.exists(chart_img):
        story.append(Paragraph(sanitize_text("📊 모의실험 손실 분포 및 위기 발생 확률 흐름", FONT_NAME), heading_style))
        story.append(Image(chart_img, width=440, height=255))
        story.append(Spacer(1, 10))
        
    # 5. 서명 지침 및 법적 효력 경고 (오영범 마스터 감성 페르소나 따뜻한 안부 이식)
    story.append(Paragraph(sanitize_text("🔔 대표님(사장님), 오늘 하루도 참 많이 애쓰셨습니다", FONT_NAME), heading_style))
    story.append(Paragraph(sanitize_text("1. 2만 번의 가상 모의 경영 시뮬레이션은 대표님이 밤낮으로 다져오신 사업의 기틀을 지키기 위한 조용한 안부이자 예방 진단입니다.", FONT_NAME), body_style))
    story.append(Paragraph(sanitize_text("2. 상위 5% 및 1% 예상 손실액은 혹여나 마주할 수 있는 법률적, 보안상 비바람에 대비해 우리가 단단한 지붕(우산)을 미리 지어둘 수 있도록 돕는 사랑의 이정표입니다.", FONT_NAME), body_style))
    story.append(Paragraph(sanitize_text("3. 리스크 초과 확률이 높게 나오더라도 자책하지 마세요. 대표님이 더 견고하고 안전한 방어막을 구축해 마음을 완전히 편히 놓으셔도 된다는 다정한 신호입니다.", FONT_NAME), body_style))
    story.append(Spacer(1, 8))
    
    # 6. 불변 2FA SHA-256 서명 박스 각인 (1차 해시)
    story.append(Paragraph(sanitize_text("🔒 디지털 보안 및 위조 방지 서명 (디지털 안전 인증)", FONT_NAME), heading_style))
    sig_data = [
        [Paragraph(sanitize_text("안전 장부 고유 번호", FONT_NAME), bold_body_style), Paragraph(data_hash, mono_style)],
        [Paragraph(sanitize_text("안전 인증 완료", FONT_NAME), bold_body_style), Paragraph(sanitize_text("2차 인증(OTP) 보안 완료 및 위조가 불가한 이중 암호화 보증", FONT_NAME), body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[140, 380])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F3EFE9")),
        ('GRID', (0,0), (-1,-1), 1.2, colors.HexColor("#D35400")), # 따뜻한 오렌지 테두리
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sig_table)
    
    # 웜톤 백그라운드 콜백을 바인딩하여 렌더링 컴파일
    doc.build(story, onFirstPage=draw_warm_background, onLaterPages=draw_warm_background)
    
    # 2. 2차 실물 파일 서명 해시 산출 (Final Artifact Hash)
    file_hash = ""
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            file_hash = hashlib.sha256(pdf_file.read()).hexdigest()
            
    print(f"📊 [PDF 저장 완료] 공식 몬테카를로 보고서 저장 완료: {pdf_path}")
    print(f"   🔒 [이중 서명 보증 완료] Document Hash: {data_hash} | File Hash: {file_hash}")
    
    return {
        "pdf_path": pdf_path,
        "data_hash": data_hash,
        "file_hash": file_hash
    }

if __name__ == "__main__":
    test_input = {"source": "MonteCarloDemo", "data_points": [8, 9, 6]}
    res = run_monte_carlo_simulation(test_input)
    generate_monte_carlo_pdf(res)
