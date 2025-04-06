"""
PaceKeeper Qt - 태그 저장소
태그 데이터 액세스 및 조작 기능
"""

from typing import List, Optional
from models.entities import Tag
from models.repository.db_manager import DBManager


class TagRepository:
    """태그 데이터 저장소 클래스"""
    
    def __init__(self, db_manager: Optional[DBManager] = None):
        """
        태그 저장소 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
        """
        self.db_manager = db_manager or DBManager()
    
    def create(self, tag: Tag) -> Tag:
        """
        새 태그 생성
        
        Args:
            tag: 저장할 태그 객체
            
        Returns:
            생성된 태그 객체 (ID 포함)
        """
        query = """
        INSERT INTO tags (name, color)
        VALUES (?, ?)
        """
        tag_id = self.db_manager.insert(query, (tag.name, tag.color))
        tag.id = tag_id
        return tag
    
    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """
        ID로 태그 조회
        
        Args:
            tag_id: 태그 ID
            
        Returns:
            조회된 태그 객체 또는 None
        """
        query = """
        SELECT id, name, color
        FROM tags
        WHERE id = ?
        """
        result = self.db_manager.fetch_one(query, (tag_id,))
        
        if result:
            return Tag(
                id=result['id'],
                name=result['name'],
                color=result['color']
            )
        return None
    
    def get_by_name(self, tag_name: str) -> Optional[Tag]:
        """
        이름으로 태그 조회
        
        Args:
            tag_name: 태그 이름
            
        Returns:
            조회된 태그 객체 또는 None
        """
        query = """
        SELECT id, name, color
        FROM tags
        WHERE name = ?
        """
        result = self.db_manager.fetch_one(query, (tag_name,))
        
        if result:
            return Tag(
                id=result['id'],
                name=result['name'],
                color=result['color']
            )
        return None
    
    def get_all(self) -> List[Tag]:
        """
        모든 태그 조회
        
        Returns:
            태그 객체 목록
        """
        query = """
        SELECT id, name, color
        FROM tags
        ORDER BY name
        """
        results = self.db_manager.fetch_all(query)
        
        return [
            Tag(
                id=result['id'],
                name=result['name'],
                color=result['color']
            )
            for result in results
        ]
    
    def update(self, tag: Tag) -> bool:
        """
        태그 정보 업데이트
        
        Args:
            tag: 업데이트할 태그 객체
            
        Returns:
            성공 여부
        """
        if tag.id is None:
            return False
        
        query = """
        UPDATE tags
        SET name = ?, color = ?
        WHERE id = ?
        """
        self.db_manager.execute_query(query, (tag.name, tag.color, tag.id))
        return True
    
    def delete(self, tag_id: int) -> bool:
        """
        태그 삭제
        
        Args:
            tag_id: 삭제할 태그 ID
            
        Returns:
            성공 여부
        """
        query = """
        DELETE FROM tags
        WHERE id = ?
        """
        self.db_manager.execute_query(query, (tag_id,))
        return True
    
    def get_or_create(self, tag_name: str, color: str = "#4a86e8") -> Tag:
        """
        태그 조회 또는 생성
        
        Args:
            tag_name: 태그 이름
            color: 태그 색상 (기본값: 파란색)
            
        Returns:
            조회되거나 생성된 태그 객체
        """
        # 태그 이름에서 # 제거
        clean_name = tag_name.strip().lstrip('#')
        
        # 이름으로 태그 조회
        tag = self.get_by_name(clean_name)
        
        # 존재하지 않으면 생성
        if tag is None:
            tag = Tag(name=clean_name, color=color)
            return self.create(tag)
        
        return tag
