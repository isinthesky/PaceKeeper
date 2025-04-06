"""
PaceKeeper Qt - 카테고리 서비스
카테고리 관련 비즈니스 로직 처리
"""

from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from app.domain.category.category_entity import CategoryEntity
from app.domain.category.category_repository import CategoryRepository


class CategoryService(QObject):
    """카테고리 서비스 클래스"""
    
    # 시그널 정의
    categoryCreated = pyqtSignal(CategoryEntity)
    categoryUpdated = pyqtSignal(CategoryEntity)
    categoryDeleted = pyqtSignal(int)  # 카테고리 ID
    categoriesChanged = pyqtSignal()  # 카테고리 목록 변경
    
    def __init__(self, category_repository: Optional[CategoryRepository] = None):
        """
        카테고리 서비스 초기화
        
        Args:
            category_repository: 카테고리 저장소 인스턴스
        """
        super().__init__()
        self.repository = category_repository or CategoryRepository()
    
    def create_category(self, name: str, description: str = "", color: str = "#4a86e8") -> CategoryEntity:
        """
        새 카테고리 생성
        
        Args:
            name: 카테고리 이름
            description: 카테고리 설명
            color: 카테고리 색상 (기본값: 파란색)
            
        Returns:
            생성된 카테고리 객체
        """
        # 이름 정제 (양쪽 공백 제거)
        clean_name = name.strip()
        
        if not clean_name:
            raise ValueError("카테고리 이름은 공백일 수 없습니다.")
        
        # 이미 존재하는 카테고리인지 확인
        existing_category = self.repository.get_by_name(clean_name)
        if existing_category:
            return existing_category
        
        # 새 카테고리 생성
        category = CategoryEntity(name=clean_name, description=description, color=color)
        created_category = self.repository.create(category)
        
        # 시그널 발생
        self.categoryCreated.emit(created_category)
        self.categoriesChanged.emit()
        
        return created_category
    
    def get_category(self, category_id: int) -> Optional[CategoryEntity]:
        """
        ID로 카테고리 조회
        
        Args:
            category_id: 카테고리 ID
            
        Returns:
            조회된 카테고리 객체 또는 None
        """
        return self.repository.get_by_id(category_id)
    
    def get_category_by_name(self, name: str) -> Optional[CategoryEntity]:
        """
        이름으로 카테고리 조회
        
        Args:
            name: 카테고리 이름
            
        Returns:
            조회된 카테고리 객체 또는 None
        """
        # 이름 정제 (양쪽 공백 제거)
        clean_name = name.strip()
        
        if not clean_name:
            return None
        
        return self.repository.get_by_name(clean_name)
    
    def get_all_categories(self) -> List[CategoryEntity]:
        """
        모든 카테고리 조회
        
        Returns:
            카테고리 객체 목록
        """
        return self.repository.get_all()
    
    def update_category(self, category: CategoryEntity) -> bool:
        """
        카테고리 정보 업데이트
        
        Args:
            category: 업데이트할 카테고리 객체
            
        Returns:
            성공 여부
        """
        if category.id is None:
            return False
        
        # 이름 정제 (양쪽 공백 제거)
        category.name = category.name.strip()
        
        if not category.name:
            raise ValueError("카테고리 이름은 공백일 수 없습니다.")
        
        # 업데이트 실행
        success = self.repository.update(category)
        
        if success:
            # 시그널 발생
            self.categoryUpdated.emit(category)
            self.categoriesChanged.emit()
        
        return success
    
    def delete_category(self, category_id: int) -> bool:
        """
        카테고리 삭제
        
        Args:
            category_id: 삭제할 카테고리 ID
            
        Returns:
            성공 여부
        """
        success = self.repository.delete(category_id)
        
        if success:
            # 시그널 발생
            self.categoryDeleted.emit(category_id)
            self.categoriesChanged.emit()
        
        return success
