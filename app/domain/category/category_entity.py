"""
PaceKeeper Qt - 카테고리 엔티티 모델
카테고리 도메인에서 사용하는 데이터 모델 클래스 정의
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CategoryEntity:
    """카테고리 데이터 클래스"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    color: str = "#FFFFFF"
    state: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """카테고리를 사전 형태로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "state": self.state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryEntity':
        """사전 데이터로부터 카테고리 객체 생성"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            color=data.get("color", "#FFFFFF"),
            state=data.get("state", 1)
        ) 