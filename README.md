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

- Python 3.x
- PyQt5 (GUI 프레임워크)
- SQLite (데이터베이스)

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

## 실행 방법

```bash
python -m pacekeeper.main
```

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