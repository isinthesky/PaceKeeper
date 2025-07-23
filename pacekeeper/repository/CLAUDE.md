# Repository Layer - CLAUDE.md

## 레이어 개요
Repository 레이어는 데이터 접근을 추상화하고 데이터 영속성을 담당하는 계층입니다. SQLAlchemy ORM을 통해 SQLite 데이터베이스와 상호작용합니다.

## 담당 임무

### 핵심 책임
- **데이터 영속성**: 데이터베이스 CRUD 연산 수행
- **쿼리 최적화**: 효율적인 데이터 조회 및 인덱싱
- **데이터 무결성**: 제약조건 및 트랜잭션 관리
- **마이그레이션**: 스키마 변경 및 데이터 마이그레이션

### 주요 컴포넌트별 역할
- **entities.py**: SQLAlchemy 모델 정의, 테이블 스키마 및 관계 설정
- **db_config.py**: 데이터베이스 연결 설정, 세션 관리
- **log_repository.py**: 작업 로그 데이터 CRUD, 통계 쿼리
- **tag_repository.py**: 태그 데이터 관리, 태그 검색 및 필터링
- **category_repository.py**: 카테고리 계층구조 데이터 관리

## 코드 작성 규칙

### 아키텍처 패턴
- **Repository 패턴**: 데이터 접근 로직을 비즈니스 로직에서 분리
- **인터페이스 구현**: 각 Repository는 해당 인터페이스를 구현 (ILogRepository, ITagRepository, ICategoryRepository)
- **의존성 주입**: DatabaseSessionManager를 생성자에서 주입받아 사용
- **Unit of Work**: 트랜잭션 단위로 작업 관리 및 데이터 일관성 보장
- **Active Record 방지**: 엔티티는 순수 데이터 모델로 유지

### 네이밍 컨벤션
```python
# 클래스명: PascalCase + Repository 접미사
class LogRepository:

# 메서드명: 데이터 액세스 패턴
def find_by_id(self, id: int) -> Optional[LogEntity]:
def find_all_by_category(self, category_id: int) -> List[LogEntity]:
def create(self, entity: LogEntity) -> LogEntity:
def update(self, entity: LogEntity) -> None:
def delete_by_id(self, id: int) -> bool:

# 쿼리 메서드: 복잡한 조건
def find_sessions_by_date_range(self, start: date, end: date) -> List[LogEntity]:
```

### 엔티티 정의 패턴
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class LogEntity(Base):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # 관계 정의
    category = relationship("CategoryEntity", back_populates="logs")
    tags = relationship("TagEntity", secondary="log_tags", back_populates="logs")
```

### 쿼리 최적화
```python
def find_logs_with_stats(self, user_id: int, limit: int = 100) -> List[LogEntity]:
    return self.session.query(LogEntity)\
        .options(joinedload(LogEntity.category))\
        .options(selectinload(LogEntity.tags))\
        .filter(LogEntity.user_id == user_id)\
        .order_by(LogEntity.start_time.desc())\
        .limit(limit)\
        .all()
```

### 트랜잭션 관리
```python
def create_session_with_tags(self, log_data: dict, tag_names: List[str]) -> LogEntity:
    try:
        # 로그 생성
        log = LogEntity(**log_data)
        self.session.add(log)
        self.session.flush()  # ID 생성을 위해
        
        # 태그 연결
        for tag_name in tag_names:
            tag = self.tag_repository.find_or_create_by_name(tag_name)
            log.tags.append(tag)
        
        self.session.commit()
        return log
    except Exception:
        self.session.rollback()
        raise
```

### 에러 처리
```python
class RepositoryError(Exception):
    pass

class EntityNotFoundError(RepositoryError):
    pass

class DuplicateEntityError(RepositoryError):
    pass

def find_by_id(self, id: int) -> LogEntity:
    entity = self.session.query(LogEntity).filter_by(id=id).first()
    if not entity:
        raise EntityNotFoundError(f"Log not found: id={id}")
    return entity
```

### 페이징 처리
```python
from typing import Tuple

def find_paginated(self, page: int, size: int) -> Tuple[List[LogEntity], int]:
    query = self.session.query(LogEntity)
    
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    return items, total
```

### 성능 고려사항
- **N+1 문제 방지**: eager loading 적극 활용
- **인덱스 활용**: 자주 조회되는 컬럼에 인덱스 설정
- **배치 처리**: bulk_insert_mappings, bulk_update_mappings 활용

### 의존성 주입 및 세션 관리
```python
# Repository 의존성 주입 예시
class CategoryRepository(ICategoryRepository):
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager  # 중앙화된 세션 관리자 주입
        self.desktop_logger = DesktopLogger("PaceKeeper")
        
    def create_category(self, name: str, description: str = "", color: str = "#FFFFFF") -> Category:
        with self.session_manager.session_scope() as session:  # 중앙화된 세션 사용
            category = Category(name=name, description=description, color=color)
            session.add(category)
            session.flush()  # ID 생성을 위해
            return category
```

### DI 컨테이너 등록
```python
# container/service_registration.py
def _register_repositories(container: "DIContainer") -> None:
    # 인터페이스와 구현체 매핑
    container.register_singleton(ILogRepository, LogRepository)
    container.register_singleton(ITagRepository, TagRepository)
    container.register_singleton(ICategoryRepository, CategoryRepository)
    
    # 인프라스트럭처 서비스
    container.register_singleton(DatabaseSessionManager, DatabaseSessionManager)
```

### 금지사항
- **비즈니스 로직 포함**: 순수 데이터 접근만 담당
- **직접 세션 생성**: DatabaseSessionManager를 통해서만 세션 접근
- **UI 또는 외부 서비스 직접 호출**: 계층 간 의존성 위반 방지
- **하드코딩된 SQL 쿼리**: ORM을 활용한 타입 안전 쿼리
- **트랜잭션 경계 외부에서 lazy loading**: 세션 스코프 밖에서 지연 로딩 방지