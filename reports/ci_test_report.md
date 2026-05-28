# ❄️ Thermal-Guard CI/CD 전사 빌드 자동화 리포트
- **검증 일시**: 2026-05-27 23:53:50
- **소요 시간**: 41.49초
- **가드레일 상태**: SUCCESS (BELOW_NORMAL CPU 활성화)
- **통과 여부**: 🔴 FAILURE 발생

## 📊 테스트 스위트별 상세 실행 내역 (총 13개)
| 스테이지 | 테스트 스위트명 | 상태 | 소요시간 (초) |
| :--- | :--- | :--- | :--- |
| Stage 1 | Developer Risk Simulator Tests | 🟢 SUCCESS | 0.46s |
| Stage 2 | Telegram Bot Integration Tests | 🟢 SUCCESS | 0.87s |
| Stage 3 | Sound Engine & Double-Send Prevention Tests | 🟢 SUCCESS | 1.64s |
| Stage 4 | Remote Control & Compliance Diagnostics Tests | 🟢 SUCCESS | 0.81s |
| Stage 5 | API Gateway Namespace Tests | 🟢 SUCCESS | 0.49s |
| Stage 6 | Core Compliance Gateway Tests | 🟢 SUCCESS | 8.37s |
| Stage 7 | Avoided Loss Router & Schema Tests | 🟢 SUCCESS | 1.09s |
| Stage 8 | Avoided Loss E2E & Integration Tests | 🟢 SUCCESS | 0.64s |
| Stage 9 | Connectivity & Security Gateway Tests | 🟢 SUCCESS | 0.51s |
| Stage 10 | Core Simulator API & Loss Calculator Tests | 🟢 SUCCESS | 0.95s |
| Stage 11 | Trend Sniper Hybrid RAG Tests | 🟢 SUCCESS | 2.83s |
| Stage 12 | Auto Planner Risk & Ctypes Cooling Tests | 🟢 SUCCESS | 7.49s |
| Stage 13 | PDF Premium Aesthetics & Cryptosystem Tests | 🔴 FAILED | 2.33s |

### 🚨 FAILED 상세 요약 로그

#### [PDF Premium Aesthetics & Cryptosystem Tests 에러]
```text
E            +  where 404 = <Response [404 Not Found]>.status_code

tests\test_pdf_premium_aesthetics.py:150: AssertionError
============================== warnings summary ===============================
tests/test_pdf_premium_aesthetics.py::test_monte_carlo_premium_pdf_and_dual_hashes
  C:\Users\user\AI ��� �γ�\�� �۾���\mini_roi_simulator\monte_carlo.py:230: UserWarning: Glyph 127922 (\N{GAME DIE}) missing from font(s) Malgun Gothic.
    plt.tight_layout()

tests/test_pdf_premium_aesthetics.py::test_monte_carlo_premium_pdf_and_dual_hashes
  C:\Users\user\AI ��� �γ�\�� �۾���\mini_roi_simulator\monte_carlo.py:232: UserWarning: Glyph 127922 (\N{GAME DIE}) missing from font(s) Malgun Gothic.
    plt.savefig(chart_path, dpi=130, facecolor=DARK_BG)

tests/test_pdf_premium_aesthetics.py::test_main_api_legal_report_ssot_double_hashing
  C:\Users\user\AppData\Local\Programs\Python\Python312\Lib\site-packages\starlette\formparsers.py:12: PendingDeprecationWarning: Please use `import python_multipart` instead.
    import multipart

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_pdf_premium_aesthetics.py::test_main_api_legal_report_ssot_double_hashing
=================== 1 failed, 2 passed, 3 warnings in 1.46s ===================
```