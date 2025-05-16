# PaceKeeper

PaceKeeper는 작업 시간과 휴식 시간을 관리하는 애플리케이션입니다. 뽀모도로 기법을 기반으로 하여 사용자가 효율적으로 작업하고 적절한 휴식을 취할 수 있도록 도와줍니다.

## 주요 기능

- 작업 시간 및 휴식 시간 타이머
- 짧은 휴식과 긴 휴식 지원
- 작업 로그 기록 및 조회
- 태그 기반 작업 분류
- 다국어 지원 (한국어, 영어)
- 사용자 설정 (타이머 시간, 소리, 색상 등)

## 기술 스택

- Python 3.11+
- PyQt5 (GUI 프레임워크)
- SQLite (데이터베이스)
- SQLAlchemy (ORM)
- PyInstaller (배포)

## 설치 및 실행

### 의존성 설치

Makefile을 사용하여 간편하게 가상 환경을 생성하고 의존성을 설치할 수 있습니다:

```bash
# 기본 의존성 설치
make install

# 개발 의존성 포함 설치 (lint 등 개발 도구 포함)
make install-dev
```

직접 가상 환경을 관리하려면 다음 명령을 사용합니다:

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치
pip install -r requirements-dev.txt
```

### 애플리케이션 실행

```bash
# Makefile을 사용한 실행
make run

# 직접 실행
python -m pacekeeper.main

# 진입점 스크립트 생성 및 실행 (더 편리한 실행)
make entry
./entry.py
```

### 애플리케이션 빌드

```bash
# 현재 플랫폼에 맞게 빌드
make build

# 특정 플랫폼용 빌드
make build-macos
make build-windows
```

## Makefile 사용법

프로젝트는 Makefile을 통해 일반적인 작업들을 자동화합니다:

| 명령어 | 설명 |
|--------|------|
| `make help` | 도움말 표시 |
| `make venv` | 가상 환경 생성 |
| `make run` | 개발 환경에서 애플리케이션 실행 |
| `make install` | 기본 의존성 설치 |
| `make install-dev` | 개발 의존성 포함 설치 |
| `make build` | 현재 플랫폼용 실행 파일 빌드 |
| `make clean` | 빌드 결과물 및 캐시 파일 정리 |
| `make lint` | 코드 문법 및 스타일 검사 |
| `make lint-fix` | 코드 문법 및 스타일 자동 수정 |
| `make dead-code` | 사용되지 않는 코드 검사 |
| `make docs` | 문서 확인 |
| `make entry` | 진입점 스크립트 생성 |
| `make clean-all` | 모든 생성 파일 및 가상 환경 정리 |

## 프로젝트 구조

```
pacekeeper/
├── __init__.py
├── main.py                  # 애플리케이션 진입점
├── consts/                  # 상수 및 설정
│   ├── labels.py            # 언어 리소스 관리
│   ├── lang_ko.json         # 한국어 리소스
│   ├── lang_en.json         # 영어 리소스
│   └── settings.py          # 애플리케이션 설정
├── controllers/             # 컨트롤러
│   ├── config_controller.py # 설정 관리
│   ├── main_controller.py   # 메인 컨트롤러
│   └── timer_controller.py  # 타이머 컨트롤러
├── views/                   # 뷰 컴포넌트
│   ├── main_window.py       # 메인 윈도우
│   ├── break_dialog.py      # 휴식 다이얼로그
│   ├── settings_dialog.py   # 설정 다이얼로그
│   └── controls.py          # 공통 UI 컴포넌트
├── repository/              # 데이터 저장소
│   ├── entities.py          # 데이터 모델
│   ├── log_repository.py    # 로그 저장소
│   ├── tag_repository.py    # 태그 저장소
│   └── category_repository.py # 카테고리 저장소
├── services/                # 서비스 레이어
│   ├── log_service.py       # 로그 서비스
│   ├── tag_service.py       # 태그 서비스
│   └── category_service.py  # 카테고리 서비스
└── utils/                   # 유틸리티
    ├── logger.py            # 로깅 유틸리티
    └── functions.py         # 공통 함수
```

## PyQt5 변환 내역

다음 파일들이 wxPython에서 PyQt5로 변환되었습니다:

1. `views/controls.py` - 공통 UI 컴포넌트 (TimerLabel, RecentLogsControl, TagButtonsPanel, TextInputPanel)
2. `views/break_dialog.py` - 휴식 다이얼로그
3. `views/settings_dialog.py` - 설정 다이얼로그
4. `views/main_window.py` - 메인 윈도우
5. `controllers/timer_controller.py` - 타이머 컨트롤러
6. `controllers/main_controller.py` - 메인 컨트롤러
7. `main.py` - 애플리케이션 진입점

## 주요 변경 사항

1. wxPython 관련 임포트를 PyQt5 임포트로 변경
2. 이벤트 처리 방식을 PyQt5의 시그널/슬롯 메커니즘으로 변경
3. 레이아웃 관리를 PyQt5 방식으로 변경
4. 위젯 생성 및 속성 설정 방식 변경
5. 다이얼로그 처리 방식 변경
6. 타이머 처리를 QTimer 기반으로 변경
7. 언어 리소스 구조 확장 및 개선

## 라이센스

MIT License

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 개발 현황

- 활발한 개발 진행 중
- 버그 리포트 및 기능 제안은 이슈 트래커를 이용해 주세요