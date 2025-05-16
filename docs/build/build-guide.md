# PaceKeeper 빌드 가이드

## 개요

PaceKeeper는 Python/PyQt5 기반의 뽀모도로 타이머 애플리케이션입니다. 이 문서는 개발 환경에서 실행 파일로 빌드하는 과정을 설명합니다.

## 사전 요구사항

- Python 3.11+
- Poetry (패키지 관리)
- PyInstaller (빌드 도구)

## 빌드 명령어

```bash
# 의존성 설치
poetry install

# 개발 모드 실행
poetry run start

# 실행 파일 빌드
make build

# 또는 직접 PyInstaller 실행
pyinstaller main-mac.spec
```

## 빌드 결과

빌드가 완료되면 `dist/` 디렉토리에 다음 파일들이 생성됩니다:
- `PaceKeeper.app` - macOS 애플리케이션 번들

## 실행 방법

```bash
# 터미널에서 실행
open dist/PaceKeeper.app

# 또는 Finder에서 더블 클릭
```

## 데이터 저장 위치

빌드된 앱은 다음 위치에 데이터를 저장합니다:
- **macOS**: `~/Library/Application Support/PaceKeeper/`
- **Windows**: `~/.pacekeeper/` (향후 구현 예정)
- **Linux**: `~/.pacekeeper/` (향후 구현 예정)

## 주요 파일 설명

### `main-mac.spec`
PyInstaller 빌드 설정 파일. 앱 번들 생성에 필요한 모든 설정을 포함합니다.

### `Makefile`
빌드 프로세스 자동화를 위한 Make 파일. 다음 타겟들을 포함합니다:
- `build`: macOS 앱 빌드
- `clean`: 빌드 결과물 정리
- `rebuild`: clean + build

### `pacekeeper/repository/db_config.py`
데이터베이스 경로를 중앙에서 관리하는 모듈. 개발/프로덕션 환경을 자동으로 감지하여 적절한 경로를 반환합니다.

## 문제 해결

### PyInstaller를 찾을 수 없음
```bash
# Poetry 환경에서 PyInstaller 설치 확인
poetry show pyinstaller

# 필요시 재설치
poetry add pyinstaller --dev
```

### 앱 실행 시 크래시
1. 디버그 로그 확인: `~/Desktop/pacekeeper_debug.log`
2. 콘솔 로그 확인: `Console.app`에서 PaceKeeper 검색
3. 권한 문제 확인: `~/Library/Application Support/` 접근 권한

### 데이터베이스 오류
- 앱은 자동으로 `~/Library/Application Support/PaceKeeper/` 디렉토리를 생성합니다
- 권한 문제가 있다면 수동으로 디렉토리 생성 후 권한 설정

## 배포 준비

### 1. 코드 서명
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/PaceKeeper.app
```

### 2. 노터라이제이션
```bash
# 앱을 압축
ditto -c -k --keepParent dist/PaceKeeper.app dist/PaceKeeper.zip

# 노터라이제이션 제출
xcrun altool --notarize-app --primary-bundle-id "com.yourcompany.pacekeeper" \
  --username "your@email.com" --password "app-specific-password" \
  --file dist/PaceKeeper.zip
```

### 3. 스테이플링
```bash
xcrun stapler staple dist/PaceKeeper.app
```

## 향후 개선사항

1. Windows/Linux 빌드 지원 추가
2. 자동 업데이트 기능 구현
3. 설치 프로그램 (DMG/MSI) 생성
4. CI/CD 파이프라인 구축