from pydantic import BaseModel, Field, validator
from typing import List, Optional

class KnowledgeAsset(BaseModel):
    """리서처가 정의한 개별 지식 자산 요소."""
    asset_type: str = Field(..., description="스킬(Skill), 도구(Tool), 템플릿 중 하나.")
    title: str = Field(..., description="학습 모듈의 핵심 개념 제목.")
    core_concept: str = Field(..., description="개념에 대한 상세 정의 및 설명. (WHY)")
    implementation_guidance: Optional[str] = Field(None, description="이 개념을 실제로 어떻게 적용할지 안내하는 구체적인 가이드라인.")

class ModuleSection(BaseModel):
    """하나의 대분류 섹션 (예: '필수 스킬' 전체)."""
    category_title: str = Field(..., description="카테고리명. (예: 데이터 권위 증명 마스터 스킬)")
    sections: List[KnowledgeAsset] = Field(..., description="해당 카테고리에 속하는 자산 목록.")

class ModuleContentRequest(BaseModel):
    """API 요청을 위한 전체 콘텐츠 구조."""
    module_name: str = Field(..., description="템플릿이 적용될 모듈의 이름 (예: 데이터 라이프사이클 진단).")
    sections: List[ModuleSection] = Field(..., description="전체 학습 모듈 섹션 목록.")

class RenderedTemplatePayload(BaseModel):
    """프론트엔드에 전송되는 최종 렌더링 구조."""
    module_name: str
    global_metadata: dict = Field(default_factory=lambda: {"theme": "Authority", "color": "#1a3d4e"})
    sections: List[dict] # 각 섹션별로 컴포넌트가 소비할 데이터만 포함