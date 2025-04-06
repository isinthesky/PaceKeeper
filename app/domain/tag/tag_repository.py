"""
PaceKeeper Qt - 태그 저장소
태그 데이터 액세스 및 조작 기능
"""

from typing import List, Optional
from app.domain.tag.tag_entity import TagEntity
from app.config.db_manager import DBManager


class TagRepository:
    """태그 데이터 저장소 클래스"""
    
    def __init__(self, db_manager: Optional[DBManager] = None):
        """
        태그 저장소 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
        """
        self.db_manager = db_manager or DBManager()
    
    def create(self, tag: TagEntity) -> TagEntity:
        """
        새 태그 생성
        
        Args:
            tag: 저장할 태그 객체
            
        Returns:
            생성된 태그 객체 (ID 포함)
        """
        query = """
        INSERT INTO tags (name, description, category_id, state)
        VALUES (?, ?, ?, ?)
        """
        tag_id = self.db_manager.insert(query, (tag.name, tag.description, tag.category_id, tag.state))
        tag.id = tag_id
        return tag
    
    def get_by_id(self, tag_id: int) -> Optional[TagEntity]:
        """
        ID로 태그 조회
        
        Args:
            tag_id: 태그 ID
            
        Returns:
            조회된 태그 객체 또는 None
        """
        query = """
        SELECT id, name, description, category_id, state
        FROM tags
        WHERE id = ?
        """
        result = self.db_manager.fetch_one(query, (tag_id,))
        
        if result:
            return TagEntity(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                category_id=result['category_id'],
                state=result['state']
            )
        return None
    
    def get_by_name(self, tag_name: str) -> Optional[TagEntity]:
        """
        이름으로 태그 조회
        
        Args:
            tag_name: 태그 이름
            
        Returns:
            조회된 태그 객체 또는 None
        """
        query = """
        SELECT id, name, description, category_id, state
        FROM tags
        WHERE name = ?
        """
        result = self.db_manager.fetch_one(query, (tag_name,))
        
        if result:
            return TagEntity(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                category_id=result['category_id'],
                state=result['state']
            )
        return None
    
    def get_all(self) -> List[TagEntity]:
        """
        모든 태그 조회
        
        Returns:
            태그 객체 목록
        """
        query = """
        SELECT id, name, description, category_id, state
        FROM tags
        ORDER BY name
        """
        results = self.db_manager.fetch_all(query)
        
        return [
            TagEntity(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                category_id=result['category_id'],
                state=result['state']
            )
            for result in results
        ]
    
    def update(self, tag: TagEntity) -> bool:
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
        SET name = ?, description = ?, category_id = ?, state = ?
        WHERE id = ?
        """
        self.db_manager.execute_query(query, (tag.name, tag.description, tag.category_id, tag.state, tag.id))
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
    
    def get_or_create(self, tag_name: str, category_id: int = 0) -> TagEntity:
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
            tag = TagEntity(name=clean_name, category_id=category_id)
            return self.create(tag)
        
        return tag
