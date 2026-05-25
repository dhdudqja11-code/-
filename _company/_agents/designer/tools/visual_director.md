# 🎨 Visual Director (비주얼 가이드 설계기)

최신 블로그 포스트 칼럼 또는 마케팅 콘텐츠를 분석하여, 이에 매칭되는 프리미엄 유튜브 썸네일 카피, 브랜드 컬러 팔레트, 폰트 매칭, 그리고 시각적 구도 레이아웃 가이드라인을 자율 기획합니다.

## 🛠️ 주요 기능
1. **네이버 칼럼 분석 연동**: `naver_writer.py`가 생성한 최신 블로그 포스팅에서 브랜드 아이덴티티 및 소제목, 이미지 지시 주석을 파싱하여 비주얼 기획에 주입합니다.
2. **프리미엄 비주얼 디렉션**: Cyberpunk Tech, Modern Space, Security Minimalist 등 세련된 디자인 언어를 반영하여 고품질 가이드라인을 설계합니다.
3. **5대 구성요소**: 큐레이션 색상(HEX/HSL), 클릭유발(CTR) 타이틀/카피 문구 3종, 3D 레이아웃 구도, 타이포그래피(Outfit/Inter/Pretendard 등) 시스템을 제공합니다.
4. **자율 백업**: `visual_guides/` 폴더 하위에 날짜별(`guide_YYYYMMDD_HHMM.md`) 마크다운 형태로 자율 백업합니다.
5. **오프라인 Mock Fallback**: LLM API 호출 불가 시 기획된 프리미엄 MOCK 디자인 지시서 가이드로 자동 폴백하여 `exit 0`으로 성공 마감합니다.

## 🚀 실행 방법
```bash
python _company/_agents/designer/tools/visual_director.py
```
