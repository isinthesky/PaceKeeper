# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 리포지토리에서 작업할 때 참고할 가이드라인입니다.

## 빌드 명령어
### 개발
- 애플리케이션 실행: `poetry run start` 또는 `python -m pacekeeper.main` 또는 `make run`
- 의존성 설치: `poetry install` 또는 `make install`
- 개발 의존성 설치: `make install-dev`
- 엔트리 스크립트 생성: `make entry` (실행 가능한 entry.py 생성)

### 테스트 및 품질 관리
- 코드 린트: `poetry run ruff check .` 또는 `make lint`
- 린트 문제 자동 수정: `poetry run ruff check --fix` 또는 `make lint-fix`
- 사용하지 않는 코드 감지: `poetry run vulture .` 또는 `make dead-code`
- 타입 체크: `poetry run ruff check .` (타입 체크 포함)

### 빌드 및 배포
- 현재 플랫폼용 빌드: `make build`
- macOS용 빌드: `make build-macos` (main-mac.spec 사용)
- Windows용 빌드: `make build-windows` (main-win.spec 사용)
- 빌드 결과물 정리: `make clean`
- 전체 정리 (가상환경 포함): `make clean-all`

## 아키텍처
PaceKeeper는 **의존성 주입(Dependency Injection)** 패턴을 적용한 **계층형 아키텍처**를 따릅니다:

### 프로젝트 구조
```
pacekeeper/
├── main.py                    # 애플리케이션 진입점 (DI 컨테이너 부트스트래핑)
├── container/                 # 의존성 주입 인프라
│   ├── di_container.py        # DI 컨테이너 (싱글톤/트랜지언트 지원)
│   └── service_registration.py # 모든 서비스 등록 관리
├── interfaces/                # 추상 인터페이스 계층
│   ├── repositories/          # Repository 인터페이스
│   │   ├── i_log_repository.py
│   │   ├── i_tag_repository.py
│   │   └── i_category_repository.py
│   └── services/              # Service 인터페이스
│       ├── i_log_service.py
│       ├── i_tag_service.py
│       └── i_category_service.py
├── database/                  # 데이터베이스 인프라
│   ├── session_manager.py     # 중앙화된 세션 관리
│   └── unit_of_work.py        # 트랜잭션 관리
├── repository/               # 데이터 접근 계층 (구현체)
│   ├── entities.py           # SQLAlchemy 데이터베이스 모델
│   ├── log_repository.py     # 작업 로그 데이터 접근
│   ├── tag_repository.py     # 태그 데이터 접근
│   └── category_repository.py # 카테고리 데이터 접근
├── services/                 # 애플리케이션 서비스 레이어 (구현체)
│   ├── log_service.py        # 작업 로그 비즈니스 로직
│   ├── tag_service.py        # 태그 관리 서비스
│   ├── category_service.py   # 카테고리 관리 서비스
│   ├── app_state_manager.py  # 애플리케이션 상태 관리
│   └── settings_manager.py   # 설정 관리 서비스
├── controllers/              # 비즈니스 로직 및 상태 관리
│   ├── main_controller.py    # 메인 애플리케이션 컨트롤러
│   ├── timer_controller.py   # 타이머 상태 및 뽀모도로 로직
│   ├── config_controller.py  # 설정 관리
│   ├── category_controls.py  # 카테고리 컨트롤러
│   └── sound_manager.py      # 사운드 시스템 관리
├── views/                    # PyQt5 UI 컴포넌트
│   ├── main_window.py        # 메인 애플리케이션 윈도우
│   ├── controls.py           # UI 컨트롤 요소
│   ├── break_dialog.py       # 휴식 알림 다이얼로그
│   ├── log_dialog.py         # 로그 관리 다이얼로그
│   ├── category_dialog.py    # 카테고리 관리 다이얼로그
│   └── settings_dialog.py    # 설정 다이얼로그
├── consts/                   # 상수 및 설정
│   ├── labels.py             # 다국어 라벨 관리자
│   ├── lang_ko.json          # 한국어 언어 파일
│   ├── lang_en.json          # 영어 언어 파일
│   └── settings.py           # 기본 설정값
├── utils/                    # 유틸리티 함수
│   ├── logger.py             # 로깅 유틸리티
│   ├── desktop_logger.py     # 데스크톱 로깅
│   ├── functions.py          # 공통 함수
│   └── resource_path.py      # 리소스 경로 관리
└── assets/                   # 정적 리소스
    ├── icons/                # 애플리케이션 아이콘
    └── sounds/               # 알림음 파일
```

### 계층별 역할
- **Container**: 의존성 주입 컨테이너와 서비스 등록 관리
- **Interfaces**: 추상 인터페이스 정의 (Repository, Service 계층)
- **Database**: 중앙화된 세션 관리 및 트랜잭션 처리
- **Repository**: SQLAlchemy를 사용한 데이터 접근 계층 → @pacekeeper/repository/CLAUDE.md
- **Services**: 애플리케이션 서비스, 도메인 로직 처리 → @pacekeeper/services/CLAUDE.md
- **Controllers**: 비즈니스 로직 및 상태 관리, View와 Service 간 중재 → @pacekeeper/controllers/CLAUDE.md
- **Views**: PyQt5 UI 컴포넌트, 사용자 인터페이스 담당 → @pacekeeper/views/CLAUDE.md
- **Utils**: 공통 유틸리티 및 헬퍼 함수
- **Consts**: 상수, 설정값, 다국어 지원
- **Assets**: 정적 리소스 (아이콘, 사운드)

## 의존성 주입 패턴
### 핵심 원칙
1. **인터페이스 기반 설계**: 모든 계층이 인터페이스에 의존
2. **자동 의존성 해결**: DIContainer가 생성자 매개변수 분석 후 자동 주입
3. **생명주기 관리**: 싱글톤과 트랜지언트 라이프사이클 지원
4. **테스트 용이성**: Mock 객체 주입으로 단위 테스트 가능

### 주요 컴포넌트
- **DIContainer**: 서비스 등록, 해결, 생명주기 관리
- **ServiceRegistry**: 모든 서비스 등록 로직 중앙화
- **DatabaseSessionManager**: 중앙화된 데이터베이스 세션 관리
- **인터페이스**: Repository와 Service 계층의 추상화

### 부트스트래핑 과정
```python
# main.py
container = DIContainer()
ServiceRegistry.register_all_services(container)
category_service = container.resolve(ICategoryService)
```

## 코드 스타일
- Python 3.11+ 타입 힌트 필수
- PEP 8 준수 및 다음 규칙 적용:
  - 변수/함수: snake_case
  - 클래스: PascalCase
  - 상수: UPPER_CASE
- 임포트 순서: 표준 라이브러리 → 서드파티 → 로컬 모듈
- 구체적인 예외 처리와 적절한 로깅 사용
- PyQt5 패턴:
  - 이벤트 처리에 시그널/슬롯 사용
  - 컨트롤러에서 GUI 직접 조작 금지
  - 소멸자에서 리소스 적절히 정리

## 테스트 도구
- 더미 데이터 생성: `make dummy-data` 또는 `python create_dummy_data.py`
- 코드 리뷰용 병합: `make merge-code` (리뷰용 통합 파일 생성)

## 다국어 지원
- 언어 파일: `pacekeeper/consts/lang_ko.json`과 `lang_en.json`
- 라벨 관리자: `pacekeeper/consts/labels.py`
- 한국어와 영어 항상 지원
- 모든 UI 텍스트에 Labels.get_label() 사용

## 데이터베이스
- **SQLAlchemy ORM**을 사용한 SQLite 데이터베이스
- **중앙화된 세션 관리**: `DatabaseSessionManager`를 통한 세션 생성 및 관리
- **트랜잭션 관리**: `UnitOfWork` 패턴으로 트랜잭션 일관성 보장
- **엔티티 정의**: `repository/entities.py`에 SQLAlchemy 모델 정의
- **Repository 패턴**: 인터페이스 기반 데이터 접근 추상화
- **도메인 분리**: 각 리포지토리는 특정 도메인 처리 (logs, tags, categories)
- **비즈니스 로직 분리**: 리포지토리는 순수 데이터 접근만, 비즈니스 로직은 서비스 레이어

## 설정
- 설정은 `config.json`에 저장
- 기본 설정은 `consts/settings.py`에 정의
- 사용자 환경설정은 `ConfigController`가 관리
- 사운드 파일: `assets/sounds/`
- 아이콘: `assets/icons/`

## 중요 사항
- 타이머는 뽀모도로 기법 따름 (25분 작업, 5분 짧은 휴식, 15분 긴 휴식)
- 휴식 알림은 가능한 경우 시스템 트레이/토스트 사용
- 휴식 유형별로 소리 알림 설정 가능
- 모든 타임스탬프는 ISO 형식으로 저장
- 태그/카테고리를 사용한 작업 세션 로깅 지원