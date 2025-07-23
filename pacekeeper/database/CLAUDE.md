# Database Layer - CLAUDE.md

## 레이어 개요
Database 레이어는 데이터베이스 연결, 세션 관리, 트랜잭션 처리를 중앙화하여 일관성 있는 데이터 접근을 제공합니다.

## 담당 임무

### 핵심 책임
- **중앙화된 세션 관리**: 모든 Repository가 공유하는 세션 관리자
- **트랜잭션 관리**: UnitOfWork 패턴을 통한 트랜잭션 일관성 보장
- **연결 풀 관리**: 데이터베이스 연결 풀 및 최적화
- **마이그레이션 지원**: 스키마 변경 및 데이터 마이그레이션

### 주요 컴포넌트별 역할
- **session_manager.py**: 중앙화된 데이터베이스 세션 생성 및 관리
- **unit_of_work.py**: 트랜잭션 범위 관리 및 커밋/롤백 처리

## 코드 작성 규칙

### 아키텍처 패턴
- **Session Manager 패턴**: 모든 세션 생성을 중앙화
- **Unit of Work 패턴**: 트랜잭션 단위로 작업 그룹화
- **Context Manager**: Python의 with 문을 활용한 자동 리소스 관리
- **Factory 패턴**: 세션 생성 로직 추상화

### 세션 관리 패턴
```python
# DatabaseSessionManager 사용법
class DatabaseSessionManager:
    def __init__(self, database_url: str = "sqlite:///pacekeeper.db"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """세션 스코프 관리"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

### Repository에서 세션 사용
```python
# Repository에서 중앙화된 세션 사용
class CategoryRepository(ICategoryRepository):
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager
        
    def create_category(self, name: str) -> Category:
        with self.session_manager.session_scope() as session:
            category = Category(name=name)
            session.add(category)
            session.flush()  # ID 생성을 위해
            return category
```

### UnitOfWork 패턴
```python
# 트랜잭션 단위 작업 관리
class UnitOfWork:
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager
        self.session = None
        
    def __enter__(self):
        self.session = self.session_manager.get_session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.session.close()
        
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()
```

### 복합 트랜잭션 처리
```python
# 여러 Repository 작업을 하나의 트랜잭션으로 처리
def complete_work_session(self, session_data: dict, tag_names: list[str]):
    with UnitOfWork(self.session_manager) as uow:
        # 로그 생성
        log = self.log_repository.create_log_with_session(session_data, uow.session)
        
        # 태그 연결
        for tag_name in tag_names:
            tag = self.tag_repository.get_or_create_tag(tag_name, uow.session)
            self.log_repository.add_tag_to_log(log.id, tag.id, uow.session)
        
        # 자동 커밋 (예외 발생 시 자동 롤백)
```

### 연결 풀 최적화
```python
# SQLAlchemy 연결 풀 설정
engine = create_engine(
    database_url,
    pool_size=10,           # 기본 연결 풀 크기
    max_overflow=20,        # 최대 추가 연결 수
    pool_recycle=3600,      # 1시간마다 연결 재생성
    pool_pre_ping=True      # 연결 유효성 사전 확인
)
```

### 에러 처리 및 복구
```python
# 데이터베이스 연결 실패 처리
try:
    with self.session_manager.session_scope() as session:
        result = session.execute(query)
        return result.fetchall()
except SQLAlchemyError as e:
    logger.error(f"Database operation failed: {e}")
    raise DatabaseConnectionError("Database access failed") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 성능 고려사항
- **연결 재사용**: 세션 풀링을 통한 연결 재사용 최적화
- **지연 로딩**: 필요한 시점까지 연관 객체 로딩 지연
- **배치 처리**: 대량 데이터 조작 시 배치 단위 처리
- **인덱스 활용**: 자주 조회되는 컬럼에 대한 인덱스 최적화

### 금지사항
- **직접 세션 생성**: Repository에서 Session() 직접 생성 금지
- **세션 누수**: 세션을 닫지 않고 방치하는 것 금지
- **긴 트랜잭션**: 장시간 실행되는 트랜잭션으로 인한 락 발생 방지
- **동시성 문제**: 동일 세션을 여러 스레드에서 공유 금지