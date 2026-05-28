@echo off
chcp 65001 > nul
echo ❄️ [Ryzen 9 / RTX 4060 쿨링 가드레일 CI 구동 중...]
set PYTHONPATH=.
python scripts/cool_ci_runner.py
pause
