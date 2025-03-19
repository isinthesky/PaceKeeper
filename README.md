# PaceKeeper

PaceKeeper는 작업과 휴식의 균형을 관리하는 스마트한 데스크톱 애플리케이션입니다.
적절한 휴식을 통해 지속 가능한 생산성을 유지하고, 업무 리듬을 최적화할 수 있도록 도와줍니다.

## 주요 기능

- 작업과 휴식의 스마트한 타이머 관리
- 맞춤형 휴식 패턴 (단기/장기 휴식) 설정
- 태그 기반 활동 로그 (#work, #break, #exercise 등)
- 직관적인 로그 분석 및 검색
  - 기간별 활동 분석
  - 태그 기반 필터링
- 데이터 안전성 (SQLite DB + 텍스트 로그)
- 개인화된 설정 관리
- 시스템 트레이 지원

## 기술 스택

- Python 3.11
- wxPython (크로스 플랫폼 GUI)
- SQLite3 (로컬 데이터베이스)
- PyInstaller (배포)
- Poetry (의존성 관리)

## 프로젝트 구조

```
pacekeeper/
├── controllers/       # 비즈니스 로직
│   ├── config_controller.py
│   └── main_controller.py
├── models/           # 데이터 관리
│   ├── data_model.py
│   └── setting_model.py
├── views/            # UI 컴포넌트
│   ├── break_dialog.py
│   ├── main_frame.py
│   ├── settings_dialog.py
│   └── track_dialog.py
├── utils.py         # 유틸리티
└── main.py         # 진입점
```

## 시작하기

1. Poetry 환경 활성화
```bash
poetry shell
```

2. 의존성 설치
```bash
poetry install
```

3. 실행
```bash
poetry run start
```

## 앱 빌드하기

```bash
pyinstaller PaceKeeper.spec -y
```
빌드된 실행 파일은 `dist` 디렉토리에서 찾을 수 있습니다.

## 데이터 관리

- 활동 기록: SQLite DB (`pace_log.db`)
- 백업: 텍스트 로그 (`pace_log.txt`)
- 설정: JSON 파일 (`config.json`)

## 로그 분석 기능

- 기간별 활동 분석: 일/주/월/연간 리포트
- 태그 기반 필터링: 작업/휴식 패턴 분석
- 데이터 시각화: 추세 및 패턴 분석
- 상세 로그 검색: 기간 + 태그 조합 검색

## 설정 옵션

- work_time: 작업 시간 (분)
- short_break: 단기 휴식 (분)
- long_break: 장기 휴식 (분)
- cycles: 장기 휴식 전 작업 사이클 수

## 라이선스

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