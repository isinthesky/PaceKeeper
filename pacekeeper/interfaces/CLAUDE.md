# Interfaces Layer - CLAUDE.md

## 레이어 개요
Interfaces 레이어는 추상 인터페이스 정의를 담당하며, 계층 간 의존성을 추상화하여 테스트성과 확장성을 향상시킵니다.

## 담당 임무

### 핵심 책임
- **계층 간 계약 정의**: Repository와 Service 계층의 추상 인터페이스 정의
- **의존성 역전**: 구체 클래스가 아닌 인터페이스에 의존하도록 설계
- **테스트 지원**: Mock 객체 주입을 통한 단위 테스트 가능
- **확장성 보장**: 새로운 구현체 추가 시 기존 코드 변경 불필요

### 주요 컴포넌트별 역할
#### repositories/
- **i_log_repository.py**: 작업 로그 데이터 접근 인터페이스
- **i_tag_repository.py**: 태그 데이터 접근 인터페이스  
- **i_category_repository.py**: 카테고리 데이터 접근 인터페이스

#### services/
- **i_log_service.py**: 작업 로그 비즈니스 로직 인터페이스
- **i_tag_service.py**: 태그 관리 서비스 인터페이스
- **i_category_service.py**: 카테고리 관리 서비스 인터페이스

## 코드 작성 규칙

### 인터페이스 정의 패턴
```python
# ABC를 활용한 추상 인터페이스 정의
from abc import ABC, abstractmethod
from pacekeeper.repository.entities import Category

class ICategoryRepository(ABC):
    """카테고리 Repository 인터페이스"""
    
    @abstractmethod
    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """카테고리 생성"""
        pass
        
    @abstractmethod
    def get_categories(self) -> list[Category]:
        """모든 활성 카테고리 조회"""
        pass
```

### 서비스 인터페이스 패턴
```python
from abc import ABC, abstractmethod
from pacekeeper.repository.entities import Category

class ICategoryService(ABC):
    """카테고리 Service 인터페이스"""
    
    @abstractmethod
    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        """새로운 카테고리 생성"""
        pass
        
    @abstractmethod
    def get_categories(self) -> list[Category]:
        """모든 활성 카테고리 조회"""
        pass
```

### 의존성 역전 원칙 적용
```python
# ❌ 잘못된 방법: 구체 클래스에 의존
class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()  # 구체 클래스에 직접 의존

# ✅ 올바른 방법: 인터페이스에 의존
class CategoryService(ICategoryService):
    def __init__(self, category_repository: ICategoryRepository):
        self.repo = category_repository  # 인터페이스에 의존
```

### 네이밍 컨벤션
- **인터페이스명**: `I` 접두사 + PascalCase + 계층명 접미사
  - Repository: `ILogRepository`, `ITagRepository`
  - Service: `ILogService`, `ITagService`
- **메서드명**: 비즈니스 액션 중심의 동사형 네이밍
  - `create_category()`, `get_categories()`, `update_category()`

### 타입 힌트 및 문서화
```python
from typing import Optional
from abc import ABC, abstractmethod

class ILogRepository(ABC):
    @abstractmethod
    def save_log(self, log: Log) -> Log:
        """
        로그를 저장합니다.
        
        Args:
            log: 저장할 로그 엔티티
            
        Returns:
            저장된 로그 엔티티 (ID 포함)
            
        Raises:
            RepositoryError: 저장 실패 시
        """
        pass
```

### 인터페이스 분리 원칙
```python
# ❌ 잘못된 방법: 거대한 인터페이스
class IBigService(ABC):
    @abstractmethod
    def log_operation(self): pass
    
    @abstractmethod 
    def tag_operation(self): pass
    
    @abstractmethod
    def category_operation(self): pass

# ✅ 올바른 방법: 책임별 인터페이스 분리
class ILogService(ABC):
    @abstractmethod
    def log_operation(self): pass
    
class ITagService(ABC):
    @abstractmethod
    def tag_operation(self): pass
```

### Mock 테스트 지원
```python
# 테스트에서 Mock 객체 사용 예시
from unittest.mock import Mock
import pytest

def test_category_service():
    # Mock Repository 생성
    mock_repo = Mock(spec=ICategoryRepository)
    mock_repo.create_category.return_value = Category(id=1, name="Test")
    
    # Service에 Mock 주입
    service = CategoryService(mock_repo)
    result = service.create_category("Test")
    
    # 검증
    assert result.name == "Test"
    mock_repo.create_category.assert_called_once()
```

### 금지사항
- **구체 타입 참조**: 인터페이스 내에서 구체 구현체 참조 금지
- **비즈니스 로직 포함**: 인터페이스는 순수 계약 정의만
- **상태 보유**: 인터페이스는 상태를 가져서는 안됨
- **플랫폼 종속**: 특정 플랫폼이나 라이브러리에 종속적인 타입 사용 금지