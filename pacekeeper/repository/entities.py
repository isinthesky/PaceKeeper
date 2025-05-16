# repository/entities.py

from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, SmallInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    """
    카테고리 엔티티 클래스
    
    태그를 그룹화하는 카테고리 정보를 저장합니다.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    description = Column(Text, nullable=False, default="")
    color = Column(String(7), nullable=False, default="#FFFFFF")
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        카테고리 객체를 딕셔너리로 변환
        
        Returns:
            카테고리 정보를 담은 딕셔너리
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "state": self.state
        }
    
    def __repr__(self) -> str:
        """
        카테고리 객체의 문자열 표현
        
        Returns:
            카테고리 정보를 담은 문자열
        """
        return f"<Category(id={self.id}, name={repr(self.name)}, description={repr(self.description)})>"


class Tag(Base):
    """
    태그 엔티티 클래스
    
    작업을 분류하는 태그 정보를 저장합니다.
    각 태그는 카테고리에 속할 수 있습니다.
    """
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    description = Column(Text, nullable=True, default="")
    category_id = Column(Integer, nullable=False, default=0)
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        태그 객체를 딕셔너리로 변환
        
        Returns:
            태그 정보를 담은 딕셔너리
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "state": self.state
        }
        
    def __repr__(self) -> str:
        """
        태그 객체의 문자열 표현
        
        Returns:
            태그 정보를 담은 문자열
        """
        return f"<Tag(id={self.id}, name={repr(self.name)}, category_id={self.category_id})>"


class Log(Base):
    """
    로그 엔티티 클래스
    
    사용자의 작업 로그 정보를 저장합니다.
    각 로그는 메시지, 태그 목록, 시작/종료 시간 등을 포함합니다.
    """
    __tablename__ = 'pace_logs'
    
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False, default="")
    tags = Column(Text, nullable=False, default="")  # JSON 형식으로 저장된 태그 ID 리스트
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    state = Column(SmallInteger, default=1)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        로그 객체를 딕셔너리로 변환
        
        Returns:
            로그 정보를 담은 딕셔너리
        """
        return {
            "id": self.id,
            "message": self.message,
            "tags": self.tags,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": self.state
        }
    
    def __repr__(self) -> str:
        """
        로그 객체의 문자열 표현
        
        Returns:
            로그 정보를 담은 문자열
        """
        return f"<Log(message={repr(self.message)}, start_date={repr(self.start_date)}, end_date={repr(self.end_date)})>"