"""
PaceKeeper Qt - 카테고리 저장소
카테고리 데이터 액세스 및 조작 기능
"""

from typing import List, Optional
from models.entities import Category
from models.repository.db_manager import DBManager


class CategoryRepository:
    """카테고리 데이터 저장소 클래스"""
    
    def __init__(self, db_manager: Optional[DBManager] = None):
        """
        카테고리 저장소 초기화
        
        Args:
            db_manager: 데이터베이스 관리자 인스턴스
        """
        self.db_manager = db_manager or DBManager()
    
    def create(self, category: Category) -> Category:
        """
        새 카테고리 생성
        
        Args:
            category: 저장할 카테고리 객체
            
        Returns:
            생성된 카테고리 객체 (ID 포함)
        """
        query = """
        INSERT INTO categories (name, description, color)
        VALUES (?, ?, ?)
        """
        category_id = self.db_manager.insert(
            query, (category.name, category.description, category.color)
        )
        category.id = category_id
        return category
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        ID로 카테고리 조회
        
        Args:
            category_id: 카테고리 ID
            
        Returns:
            조회된 카테고리 객체 또는 None
        """
        query = """
        SELECT id, name, description, color
        FROM categories
        WHERE id = ?
        """
        result = self.db_manager.fetch_one(query, (category_id,))
        
        if result:
            return Category(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                color=result['color']
            )
        return None
    
    def get_by_name(self, category_name: str) -> Optional[Category]:
        """
        이름으로 카테고리 조회
        
        Args:
            category_name: 카테고리 이름
            
        Returns:
            조회된 카테고리 객체 또는 None
        """
        query = """
        SELECT id, name, description, color
        FROM categories
        WHERE name = ?
        """
        result = self.db_manager.fetch_one(query, (category_name,))
        
        if result:
            return Category(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                color=result['color']
            )
        return None
    
    def get_all(self) -> List[Category]:
        """
        모든 카테고리 조회
        
        Returns:
            카테고리 객체 목록
        """
        query = """
        SELECT id, name, description, color
        FROM categories
        ORDER BY name
        """
        results = self.db_manager.fetch_all(query)
        
        return [
            Category(
                id=result['id'],
                name=result['name'],
                description=result['description'],
                color=result['color']
            )
            for result in results
        ]
    
    def update(self, category: Category) -> bool:
        """
        카테고리 정보 업데이트
        
        Args:
            category: 업데이트할 카테고리 객체
            
        Returns:
            성공 여부
        """
        if category.id is None:
            return False
        
        query = """
        UPDATE categories
        SET name = ?, description = ?, color = ?
        WHERE id = ?
        """
        self.db_manager.execute_query(
            query, 
            (category.name, category.description, category.color, category.id)
        )
        return True
    
    def delete(self, category_id: int) -> bool:
        """
        카테고리 삭제
        
        Args:
            category_id: 삭제할 카테고리 ID
            
        Returns:
            성공 여부
        """
        query = """
        DELETE FROM categories
        WHERE id = ?
        """
        self.db_manager.execute_query(query, (category_id,))
        return True
