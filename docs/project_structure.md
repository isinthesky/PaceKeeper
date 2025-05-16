# PaceKeeper 프로젝트 구조

## 개요

PaceKeeper는 뽀모도로 기법 기반의 시간 관리 애플리케이션으로, 효율적인 작업과 휴식 관리를 위한 다양한 기능을 제공합니다. 이 문서는 PaceKeeper의 코드 구조와 아키텍처를 상세히 설명합니다.

## 아키텍처 개요

PaceKeeper는 **MVC(Model-View-Controller)** 아키텍처 패턴을 따르며, 이를 Repository-Service-Controller-View 계층으로 확장하여 구현했습니다. 이 구조는 관심사의 분리와 코드 재사용성을 극대화합니다.

![아키텍처 다이어그램](https://via.placeholder.com/800x400?text=PaceKeeper+Architecture+Diagram)

## 디렉토리 구조

```
pacekeeper/
├── __init__.py
├── main.py                  # 애플리케이션 진입점
├── const.py                 # 전역 상수 정의
├── assets/                  # 리소스 파일(아이콘, 소리 등)
├── consts/                  # 상수 및 설정 관련 모듈
├── controllers/             # 컨트롤러 계층 - 비즈니스 로직 처리
├── repository/              # 데이터 액세스 계층 - DB 연동
├── services/                # 서비스 계층 - 비즈니스 로직과 데이터 계층 연결
├── utils/                   # 유틸리티 함수 및 클래스
└── views/                   # 뷰 계층 - 사용자 인터페이스
```

### 각 디렉토리 상세 설명

#### 1. 애플리케이션 진입점
- **main.py**: PaceKeeper 애플리케이션의 시작점으로, PyQt5 애플리케이션 객체를 초기화하고 메인 윈도우를 생성합니다.

#### 2. 상수 및 설정 (consts/)
- **labels.py**: 다국어 지원을 위한 언어 리소스 관리
- **lang_ko.json**: 한국어 언어 리소스
- **lang_en.json**: 영어 언어 리소스
- **settings.py**: 기본 설정값 및 설정 관련 상수

#### 3. 컨트롤러 계층 (controllers/)
- **main_controller.py**: 애플리케이션의 핵심 로직을 조정하는 메인 컨트롤러
- **config_controller.py**: 설정 관리 컨트롤러 (싱글톤 패턴 적용)
- **timer_controller.py**: 타이머 기능 관리 컨트롤러
- **timer_thread.py**: 타이머 스레드 구현
- **sound_manager.py**: 소리 알림 관리 컨트롤러
- **category_controls.py**: 카테고리 기능 관리 컨트롤러

#### 4. 레포지토리 계층 (repository/)
- **entities.py**: SQLAlchemy ORM 모델 정의 (Category, Tag, Log)
- **log_repository.py**: 작업 로그 데이터 액세스 객체
- **tag_repository.py**: 태그 데이터 액세스 객체
- **category_repository.py**: 카테고리 데이터 액세스 객체

#### 5. 서비스 계층 (services/)
- **log_service.py**: 작업 로그 관련 비즈니스 로직
- **tag_service.py**: 태그 관련 비즈니스 로직
- **category_service.py**: 카테고리 관련 비즈니스 로직
- **setting_model.py**: 설정 데이터 모델 및 관리 로직

#### 6. 뷰 계층 (views/)
- **main_window.py**: 애플리케이션 메인 윈도우 UI
- **main_frame.py**: 메인 윈도우의 중앙 프레임 UI
- **break_dialog.py**: 휴식 시간 다이얼로그 UI
- **settings_dialog.py**: 설정 다이얼로그 UI
- **log_dialog.py**: 로그 조회 다이얼로그 UI
- **category_dialog.py**: 카테고리 관리 다이얼로그 UI
- **controls.py**: 공통 UI 컴포넌트 (TimerLabel, RecentLogsControl 등)

#### 7. 유틸리티 (utils/)
- **functions.py**: 공통 유틸리티 함수 (리소스 경로 관리, 태그 추출 등)
- **logger.py**: 로깅 유틸리티
- **desktop_logger.py**: 데스크톱 환경 로깅 특화 유틸리티

## 주요 클래스 및 관계

### 컨트롤러 계층
1. **ConfigController (싱글톤)**
   - 애플리케이션 설정 관리
   - 애플리케이션 상태(AppStatus) 관리
   - 타이머 사이클 추적

2. **MainController**
   - 메인 윈도우와 ConfigController 연결
   - 타이머 세션 관리(학습/휴식)
   - 서비스 레이어와 상호작용하여 데이터 처리
   - 소리 알림 트리거

3. **TimerService**
   - 카운트다운 타이머 관리
   - 일시정지/재개 기능 제공
   - 타이머 완료 콜백 처리

4. **SoundManager**
   - 소리 리소스 로드 및 재생
   - 설정에 따른 소리 알림 제어

### 서비스 계층
1. **LogService**
   - 작업 로그 생성, 조회, 검색 기능
   - LogRepository와 상호작용

2. **TagService**
   - 태그 생성, 조회, 관리 기능
   - TagRepository와 상호작용

3. **CategoryService**
   - 카테고리 생성, 조회, 관리 기능
   - CategoryRepository와 상호작용

### 레포지토리 계층
1. **ORM 엔티티**
   - Category: 카테고리 데이터 모델
   - Tag: 태그 데이터 모델
   - Log: 작업 로그 데이터 모델

2. **Repository 클래스**
   - SQLAlchemy 세션 관리
   - CRUD 연산 제공
   - 데이터 쿼리 및 필터링 기능

### 뷰 계층
1. **MainWindow**
   - 애플리케이션의 주요 UI 컨테이너
   - 메뉴, 상태바, 중앙 위젯 관리

2. **BreakDialog**
   - 휴식 시간 알림 및 카운트다운 표시
   - 휴식 종료 콜백 처리

3. **SettingsDialog**
   - 사용자 설정 인터페이스
   - 설정 변경 및 저장 기능

4. **공통 컨트롤**
   - TimerLabel: 타이머 표시 컴포넌트
   - RecentLogsControl: 최근 로그 표시 컴포넌트
   - TagButtonsPanel: 태그 선택 버튼 컴포넌트
   - TextInputPanel: 작업 입력 컴포넌트

## 데이터 흐름

1. **설정 데이터 흐름**
   - 설정 파일(config.json) ↔ ConfigController ↔ SettingsDialog ↔ 사용자

2. **타이머 데이터 흐름**
   - ConfigController → MainController → TimerService → UI 업데이트
   - 타이머 완료 → 상태 변경 → 소리 알림 → 다음 세션 시작

3. **로그 데이터 흐름**
   - 사용자 입력 → MainController → LogService → LogRepository → 데이터베이스
   - 데이터베이스 → LogRepository → LogService → MainController → UI 표시

4. **태그/카테고리 데이터 흐름**
   - 사용자 관리 → Service → Repository → 데이터베이스
   - 데이터베이스 → Repository → Service → UI 표시

## 주요 기능 구현 상세

### 1. 타이머 시스템
- **TimerService**가 PyQt5의 `QTimer`를 활용하여 타이머 기능 제공
- 타이머 상태 변경 시 콜백 시스템을 통해 UI 업데이트 및 다음 단계 진행
- 타이머 일시정지/재개는 내부 상태와 타이머 객체 제어를 통해 구현

### 2. 로그 관리 시스템
- SQLAlchemy ORM을 사용하여 로그 데이터 관리
- 태그 추출 및 연결 기능을 통해 작업 분류
- 로그 조회 시 필터링 및 정렬 기능 제공

### 3. 다국어 지원 시스템
- JSON 파일 기반의 언어 리소스 관리
- `labels.py`의 `load_language_resource` 함수를 통한 언어 리소스 로드
- UI 컴포넌트에 언어 리소스 적용

### 4. 설정 관리 시스템
- JSON 파일 기반의 설정 저장 및 로드
- 메모리 내 설정 캐싱으로 성능 최적화
- 싱글톤 패턴을 적용한 ConfigController로 일관된 설정 액세스

## 기술 스택

- **언어**: Python 3.11+
- **GUI 프레임워크**: PyQt5 5.15.9
- **데이터베이스 ORM**: SQLAlchemy 2.0.38
- **패키지 관리**: Poetry
- **빌드 도구**: PyInstaller
- **사운드 처리**: Pygame 2.6.1
- **디버깅**: icecream 2.1.3
- **정적 분석**: Ruff 0.8.4, Vulture 2.14

## 확장성 및 유지보수성

1. **모듈화된 구조**
   - 기능별 분리된 모듈 구조로 코드 변경 영향 최소화
   - 계층별 명확한 책임 분리로 테스트 및 디버깅 용이

2. **설정 기반 동작**
   - 하드코딩된 값 대신 설정 파일 사용으로 유연성 확보
   - 런타임에 설정 변경 가능성 제공

3. **인터페이스 중심 설계**
   - 컴포넌트 간 결합도 최소화로 대체 구현 용이
   - 명확한 API를 통한 컴포넌트 통신

4. **MVC 패턴 준수**
   - 관심사 분리로 코드 이해도 및 유지보수성 향상
   - UI 변경과 비즈니스 로직 변경의 독립적 수행 가능

이 문서는 PaceKeeper의 전체 구조와 주요 구성 요소에 대한 상세한 이해를 제공하여, 개발자가 프로젝트를 효과적으로 개선하고 확장할 수 있도록 지원합니다.