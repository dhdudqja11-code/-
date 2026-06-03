import sys
import os

# 개발 에이전트 내부의 'src' 디렉토리 절대 경로 획득
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
