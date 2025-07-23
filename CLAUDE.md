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
PaceKeeper는 관심사 분리가 명확한 MVC 아키텍처를 따릅니다:

### 프로젝트 구조
```
pacekeeper/
├── main.py                    # 애플리케이션 진입점
├── assets/                    # 정적 리소스
│   ├── icons/                 # 애플리케이션 아이콘 (PaceKeeper.icns, .ico, .png)
│   └── sounds/                # 알림음 파일 (알람, 휴식 등)
├── consts/                    # 상수 및 설정
│   ├── labels.py             # 다국어 라벨 관리자
│   ├── lang_ko.json          # 한국어 언어 파일
│   ├── lang_en.json          # 영어 언어 파일
│   └── settings.py           # 기본 설정값
├── controllers/              # 비즈니스 로직 및 상태 관리
│   ├── main_controller.py    # 메인 애플리케이션 컨트롤러
│   ├── timer_controller.py   # 타이머 상태 및 뽀모도로 로직
│   ├── config_controller.py  # 설정 관리
│   ├── category_controls.py  # 카테고리 컨트롤러
│   ├── sound_manager.py      # 사운드 시스템 관리
│   └── timer_thread.py       # 타이머 스레드 처리
├── repository/               # 데이터 접근 계층
│   ├── entities.py           # SQLAlchemy 데이터베이스 모델
│   ├── db_config.py          # 데이터베이스 연결 설정
│   ├── log_repository.py     # 작업 로그 데이터 접근
│   ├── tag_repository.py     # 태그 데이터 접근
│   └── category_repository.py # 카테고리 데이터 접근
├── services/                 # 애플리케이션 서비스 레이어
│   ├── log_service.py        # 작업 로그 비즈니스 로직
│   ├── tag_service.py        # 태그 관리 서비스
│   ├── category_service.py   # 카테고리 관리 서비스
│   ├── app_state_manager.py  # 애플리케이션 상태 관리
│   ├── setting_model.py      # 설정 모델
│   └── settings_manager.py   # 설정 관리 서비스
├── utils/                    # 유틸리티 함수
│   ├── logger.py             # 로깅 유틸리티
│   ├── desktop_logger.py     # 데스크톱 로깅
│   ├── functions.py          # 공통 함수
│   └── resource_path.py      # 리소스 경로 관리
└── views/                    # PyQt5 UI 컴포넌트
    ├── main_window.py        # 메인 애플리케이션 윈도우 (미니 모드 지원)
    ├── controls.py           # UI 컨트롤 요소
    ├── break_dialog.py       # 휴식 알림 다이얼로그
    ├── log_dialog.py         # 로그 관리 다이얼로그
    ├── category_dialog.py    # 카테고리 관리 다이얼로그
    └── settings_dialog.py    # 설정 다이얼로그
```

### 계층별 역할
- **Views**: PyQt5 UI 컴포넌트, 사용자 인터페이스 담당 → @pacekeeper/views/CLAUDE.md
- **Controllers**: 비즈니스 로직 및 상태 관리, View와 Service 간 중재 → @pacekeeper/controllers/CLAUDE.md
- **Services**: 애플리케이션 서비스, 도메인 로직 처리 → @pacekeeper/services/CLAUDE.md
- **Repository**: SQLAlchemy를 사용한 데이터 접근 계층 → @pacekeeper/repository/CLAUDE.md
- **Utils**: 공통 유틸리티 및 헬퍼 함수
- **Consts**: 상수, 설정값, 다국어 지원
- **Assets**: 정적 리소스 (아이콘, 사운드)

핵심 컴포넌트:
- `main.py`: 애플리케이션 진입점, Qt 앱과 컨트롤러 초기화
- `main_window.py`: 타이머와 컨트롤이 있는 메인 애플리케이션 윈도우 (미니 모드 지원)
- `timer_controller.py`: 타이머 상태와 휴식 로직 관리 (뽀모도로 기법)
- `config_controller.py`: 애플리케이션 설정 및 지속성 처리

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
- SQLAlchemy ORM을 사용한 SQLite 데이터베이스
- 엔티티는 `repository/entities.py`에 정의
- 각 리포지토리는 특정 도메인 처리 (logs, tags, categories)
- 비즈니스 로직은 리포지토리가 아닌 서비스 레이어에서 처리

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