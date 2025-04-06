"""
PaceKeeper Qt - 로그 엔티티 모델
로그 도메인에서 사용하는 데이터 모델 클래스 정의
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class LogEntity:
    """로그 항목 데이터 클래스"""
    id: Optional[int] = None
    message: str = ""
    tags: str = ""
    start_date: str = ""
    end_date: Optional[str] = None
    state: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """로그 항목을 사전 형태로 변환"""
        return {
            "id": self.id,
            "message": self.message,
            "tags": self.tags,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": self.state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntity':
        """사전 데이터로부터 로그 항목 객체 생성"""
        return cls(
            id=data.get("id"),
            message=data.get("message", ""),
            tags=data.get("tags", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date"),
            state=data.get("state", 1)
        ) 