# BreakTrack

BreakTrack는 휴식 시간을 추적·관리하기 위한 데스크톱 애플리케이션입니다.
공부나 업무 중 규칙적으로 휴식을 취해 집중력을 높이고, 휴식 시간을 로그로 남겨 기록·분석할 수 있도록 돕습니다.

## 주요 기능

- 작업(공부) 시간과 휴식 시간의 반복 타이머
- 단축 휴식(short break), 장기 휴식(long break) 등 다양한 휴식 패턴 지정
- Tag(#태그) 기반 휴식 로그 관리
    - 예)#rest, #study, #exercise 등 사용자가 원하는 태그를 붙여 기록
- TrackDialog를 통한 휴식(작업) 로그 조회
- 기간 검색(예: 2024-01-01 ~ 2024-01-31)
- 태그 검색(예: #study, #rest)
- SQLite 데이터베이스 + 텍스트 로그 병행 저장
- 사용자 설정(작업 시간, 휴식 시간, 사이클 수 등) 관리
- 윈도우 시스템 트레이 아이콘(선택사항) 지원

## 기술 스택

- Python 3.11
- wxPython (GUI) : OS를 가리지 않는 자연스러운 GUI, PyInstaller와 호환성, 배포 용량
- SQLite3 (데이터베이스) : local database
- PyInstaller (배포)
- Poetry (의존성 관리)

## 프로젝트 구조

```
breaktrack/
├── controllers/         # 컨트롤러 
│   ├── config_controller.py
│   └── main_controller.py
├── models/             # 데이터 모델
│   ├── data_model.py
│   └── setting_model.py  
├── views/              # UI 뷰
│   ├── break_dialog.py
│   ├── main_frame.py
│   ├── settings_dialog.py
│   └── track_dialog.py
├── utils.py           # 유틸리티 함수
└── main.py           # 진입점
```

- controllers: 전체 로직 흐름 및 이벤트 핸들링 (타이머, 상태 전환 등)
- models: 데이터 접근과 저장 (SQLite, 텍스트 로그, 설정 파일 등)
- views: wxPython 기반 UI 코드 (Frame, Dialog, ListCtrl 등)
- utils.py: 리소스 경로 처리, 태그 파싱 등 범용 유틸

## 설치 방법

1. poetry 가상 환경 실행
```bash
poetry shell
```

2. Poetry를 사용한 의존성 설치:
```bash
poetry install
```

3. 개발 환경에서 실행:
```bash
poetry run start
```

## 배포

PyInstaller를 사용하여 실행 파일 생성:

```bash
pyinstaller main.spec
```

생성된 실행 파일은 `dist` 디렉토리에서 찾을 수 있습니다.

## 데이터 저장

- SQLite 데이터베이스 (`break_log.db`): 휴식 기록 영구 저장
- 텍스트 로그 파일 (`break_log.txt`): 백업용 텍스트 로그


## TrackDialog 상세

**track_dialog.py**는 휴식 로그를 조회·검색하는 UI 다이얼로그입니다.

- 날짜 검색: 시작일/종료일을 지정하거나 버튼을 통해 지난 1년/3달/1달/1주/1일 내역 등을 간편 조회
- 태그 검색: #study, #rest 같은 태그를 입력하면 해당 태그가 포함된 로그만 필터링
- 검색 결과는 wxPython의 ListCtrl을 통해 테이블 형태로 화면에 표시
- 기간·태그 두 조건을 모두 입력하면 교집합(AND 조건)으로 필터링


## 설정 관리

SettingsDialog(settings_dialog.py)에서 다음 값들을 GUI로 설정 가능:
- study_time: 작업(공부) 시간 (분)
- short_break: 짧은 휴식 시간 (분)
- long_break: 긴 휴식 시간 (분)
- cycles: 몇 회 작업 후 긴 휴식을 할지

설정은 **setting_model.py**를 통해 JSON 파일(config.json)로 저장/로드됩니다.

## 사용 예시

1. 앱 실행: poetry run start
2.	메인 화면에서 ‘시작’ 버튼 → 작업 타이머가 시작
3.	작업 시간 종료 시, BreakDialog가 표시되어 휴식 시간 카운트다운 진행
4.	휴식 종료 시, 메시지·태그를 입력하면 DB에 기록
5.	메뉴 → “기록 보기” 선택 → TrackDialog 창에서 기간/태그 검색 가능

## 라이선스

MIT License

## 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 주의사항

- 개발 중인 프로젝트이므로 예기치 않은 버그가 있을 수 있습니다
- 이슈 트래커를 통해 버그를 보고해주세요