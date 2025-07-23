# Container Layer - CLAUDE.md

## 레이어 개요
Container 레이어는 의존성 주입(Dependency Injection) 인프라를 담당하며, 모든 서비스의 등록, 해결, 생명주기 관리를 처리합니다.

## 담당 임무

### 핵심 책임
- **서비스 등록**: 인터페이스와 구현체의 매핑 관리
- **의존성 해결**: 생성자 매개변수 분석을 통한 자동 의존성 주입
- **생명주기 관리**: 싱글톤과 트랜지언트 라이프사이클 지원
- **순환 의존성 감지**: 의존성 그래프 분석을 통한 순환 참조 방지

### 주요 컴포넌트별 역할
- **di_container.py**: DI 컨테이너 구현체, 서비스 등록 및 해결
- **service_registration.py**: 모든 서비스 등록 로직 중앙화

## 코드 작성 규칙

### 아키텍처 패턴
- **Service Locator 패턴**: 중앙화된 서비스 레지스트리
- **Factory 패턴**: 의존성 그래프를 분석하여 인스턴스 생성
- **Singleton 관리**: 생명주기에 따른 인스턴스 캐싱
- **Reflection 활용**: 타입 힌트 분석을 통한 자동 의존성 해결

### DI 컨테이너 사용법
```python
# 서비스 등록
container = DIContainer()
container.register_singleton(ILogService, LogService)
container.register_transient(MainController, MainController)

# 서비스 해결
log_service = container.resolve(ILogService)  # 자동 의존성 주입
```

### 서비스 등록 패턴
```python
# service_registration.py
class ServiceRegistry:
    @staticmethod
    def register_all_services(container: "DIContainer") -> None:
        # Repository 계층
        container.register_singleton(ILogRepository, LogRepository)
        
        # Service 계층  
        container.register_singleton(ILogService, LogService)
        
        # 인프라스트럭처
        container.register_singleton(DatabaseSessionManager, DatabaseSessionManager)
```

### 생명주기 관리
- **Singleton**: 애플리케이션 전체에서 하나의 인스턴스만 생성
- **Transient**: 매번 새로운 인스턴스 생성
- **자동 감지**: 생성자 매개변수 타입 힌트 분석으로 의존성 주입

### 에러 처리
```python
# 등록되지 않은 서비스 요청
try:
    service = container.resolve(UnregisteredService)
except ValueError as e:
    logger.error(f"Service not registered: {e}")

# 순환 의존성 감지
if self._has_circular_dependency(interface, visited):
    raise ValueError(f"Circular dependency detected: {interface}")
```

### 성능 고려사항
- **지연 생성**: 실제 요청 시점까지 인스턴스 생성 지연
- **캐싱**: 싱글톤 인스턴스 캐싱으로 재사용
- **타입 분석**: 런타임 타입 힌트 분석 최적화

### 금지사항
- **하드코딩된 의존성**: 모든 의존성은 컨테이너를 통해 관리
- **순환 의존성**: 클래스 간 순환 참조 생성 금지
- **직접 인스턴스화**: 컨테이너 외부에서 서비스 직접 생성 금지
- **런타임 등록**: 애플리케이션 시작 후 서비스 등록 변경 금지