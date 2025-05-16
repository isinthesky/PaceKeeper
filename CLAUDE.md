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
- **Views**: PyQt5 UI 컴포넌트 (main_window, dialogs, controls)
- **Controllers**: 비즈니스 로직 및 상태 관리 (main_controller, timer_controller, config_controller)
- **Services**: 애플리케이션 서비스 (log_service, tag_service, category_service)
- **Repository**: SQLAlchemy를 사용한 데이터 접근 계층 (log_repository, tag_repository, category_repository)
- **Entities**: 데이터베이스 테이블을 위한 SQLAlchemy 모델

핵심 컴포넌트:
- `main.py`: 애플리케이션 진입점, Qt 앱과 컨트롤러 초기화
- `main_window.py`: 타이머와 컨트롤이 있는 메인 애플리케이션 윈도우
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