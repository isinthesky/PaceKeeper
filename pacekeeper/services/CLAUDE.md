# Services Layer - CLAUDE.md

## 레이어 개요
Services 레이어는 애플리케이션의 핵심 비즈니스 로직을 처리하며, Repository와 Controller 간의 중간 계층 역할을 수행합니다.

## 담당 임무

### 핵심 책임
- **도메인 로직**: 비즈니스 규칙과 워크플로우 구현
- **데이터 변환**: Repository 데이터를 애플리케이션 모델로 변환
- **트랜잭션 관리**: 복합적인 데이터 조작 시 일관성 보장
- **유효성 검증**: 입력 데이터의 비즈니스 규칙 검증

### 주요 컴포넌트별 역할
- **log_service.py**: 작업 세션 로깅, 통계 계산, 히스토리 관리
- **tag_service.py**: 태그 생성/수정/삭제, 태그 기반 검색 및 필터링
- **category_service.py**: 카테고리 계층 구조 관리, 분류 로직
- **app_state_manager.py**: 전역 애플리케이션 상태 관리
- **settings_manager.py**: 설정값 검증, 기본값 처리, 설정 마이그레이션
- **setting_model.py**: 설정 데이터 모델과 타입 정의

## 코드 작성 규칙

### 아키텍처 패턴
- **도메인 중심 설계**: 비즈니스 로직을 도메인별로 분리
- **의존성 역전**: Repository 인터페이스에 의존, 구현체는 주입
- **순수 함수 지향**: 가능한 한 부작용 없는 함수 작성

### 네이밍 컨벤션
```python
# 클래스명: PascalCase + Service 접미사
class LogService:

# 메서드명: 비즈니스 액션 중심
def create_work_session(self, tag: str, category: str) -> WorkSession:
def calculate_productivity_stats(self, period: DateRange) -> ProductivityStats:

# 검증 메서드: validate_ 접두사
def validate_tag_name(self, name: str) -> ValidationResult:
```

### 데이터 검증 패턴
```python
def create_category(self, name: str, parent_id: Optional[int] = None) -> Category:
    # 입력 검증
    if not name or len(name.strip()) == 0:
        raise InvalidCategoryNameError("카테고리 이름은 필수입니다")
    
    if len(name) > MAX_CATEGORY_NAME_LENGTH:
        raise InvalidCategoryNameError(f"카테고리 이름은 {MAX_CATEGORY_NAME_LENGTH}자를 초과할 수 없습니다")
    
    # 중복 검사
    if self.repository.exists_by_name(name, parent_id):
        raise DuplicateCategoryError(f"'{name}' 카테고리가 이미 존재합니다")
    
    return self.repository.create(name, parent_id)
```

### 트랜잭션 관리
```python
@transactional
def complete_work_session(self, session_id: int, tags: List[str]) -> None:
    session = self.log_repository.get_by_id(session_id)
    session.end_time = datetime.now()
    
    # 태그 연결
    for tag_name in tags:
        tag = self.tag_service.get_or_create(tag_name)
        self.log_repository.add_tag(session_id, tag.id)
    
    self.log_repository.update(session)
```

### 에러 처리
```python
# 도메인별 커스텀 예외 사용
class TagServiceError(Exception):
    pass

class DuplicateTagError(TagServiceError):
    pass

class TagNotFoundError(TagServiceError):
    pass

# 예외 체인 활용
try:
    return self.repository.create_tag(name)
except RepositoryError as e:
    raise TagServiceError(f"태그 생성 실패: {name}") from e
```

### 로깅 패턴
```python
# 비즈니스 이벤트 중심 로깅
logger.info(f"작업 세션 생성: category={category}, estimated_duration={duration}")
logger.warning(f"중복 태그 생성 시도: name={name}")
logger.debug(f"생산성 통계 계산 완료: {stats}")
```

### 성능 고려사항
- **지연 로딩**: 필요한 시점까지 데이터 로드 지연
- **캐싱**: 자주 조회되는 데이터의 메모리 캐싱
- **배치 처리**: 대량 데이터 처리 시 배치 단위 처리

### 금지사항
- UI 코드나 PyQt5 위젯 직접 참조
- 파일 시스템 직접 접근 (Repository를 통해)
- 하드코딩된 비즈니스 규칙 (설정이나 상수 사용)
- 동시성 제어 없는 공유 상태 변경