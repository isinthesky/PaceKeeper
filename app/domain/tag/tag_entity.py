"""
PaceKeeper Qt - 태그 엔티티 모델
태그 도메인에서 사용하는 데이터 모델 클래스 정의
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class TagEntity:
    """태그 데이터 클래스"""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    category_id: Optional[int] = None
    state: int = 1
    # 카테고리 색상을 저장할 속성 추가
    category_color: str = "#FFFFFF"

    def to_dict(self) -> Dict[str, Any]:
        """태그를 사전 형태로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "state": self.state,
            "category_color": self.category_color,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TagEntity":
        """사전 데이터로부터 태그 객체 생성"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category_id=data.get("category_id"),
            state=data.get("state", 1),
            category_color=data.get("category_color", "#FFFFFF"),
        )
