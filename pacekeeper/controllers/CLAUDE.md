# Controllers Layer - CLAUDE.md

## 레이어 개요
Controllers 레이어는 비즈니스 로직과 상태 관리를 담당하며, Views와 Services 간의 중재자 역할을 수행합니다.

## 담당 임무

### 핵심 책임
- **상태 관리**: 애플리케이션의 전체적인 상태와 데이터 흐름 제어
- **비즈니스 로직**: 도메인별 핵심 업무 규칙과 프로세스 구현
- **View-Service 중재**: UI 이벤트를 받아 적절한 서비스 호출 후 View 업데이트
- **이벤트 처리**: 사용자 액션과 시스템 이벤트에 대한 응답 처리

### 주요 컴포넌트별 역할
- **main_controller.py**: 전체 애플리케이션 생명주기와 메인 워크플로우 관리
- **timer_controller.py**: 뽀모도로 타이머 로직, 휴식 알림, 세션 상태 관리
- **config_controller.py**: 사용자 설정의 로드/저장, 설정 변경 이벤트 처리
- **category_controls.py**: 카테고리 CRUD 작업과 UI 연동
- **sound_manager.py**: 사운드 재생 로직과 볼륨/음성 설정 관리
- **timer_thread.py**: 백그라운드 타이머 스레드와 메인 스레드 간 통신

## 코드 작성 규칙

### 아키텍처 패턴
- **의존성 주입**: 생성자를 통한 서비스 의존성 주입
- **단일 책임**: 각 컨트롤러는 하나의 도메인 영역만 담당
- **이벤트 기반**: PyQt5 시그널/슬롯을 활용한 느슨한 결합

### 네이밍 컨벤션
```python
# 클래스명: PascalCase + Controller 접미사
class TimerController:

# 메서드명: snake_case, 액션 위주 네이밍
def start_timer(self) -> None:
def handle_break_finished(self, break_type: str) -> None:

# 시그널 처리 메서드: on_ 접두사
def on_timer_expired(self) -> None:
def on_settings_changed(self, key: str, value: Any) -> None:
```

### 에러 처리
```python
# 구체적인 예외 타입 사용
try:
    self.timer_service.start_session()
except TimerAlreadyRunningError:
    self.show_warning("타이머가 이미 실행 중입니다")
except ConfigurationError as e:
    logger.error(f"설정 오류: {e}")
    self.request_config_reset()
```

### 로깅 패턴
```python
# 구조화된 로깅 (상태 변화, 중요 이벤트)
logger.info(f"타이머 시작: session_type={session_type}, duration={duration}")
logger.debug(f"설정 업데이트: {key}={old_value} → {new_value}")
```

### View 상호작용 규칙
- **직접 UI 조작 금지**: View 메서드를 통한 간접 조작만 허용
- **데이터 바인딩**: 상태 변경 시 즉시 View에 반영
- **비동기 처리**: 긴 작업은 별도 스레드에서 처리 후 시그널로 결과 전달

### 금지사항
- Repository 직접 접근 (반드시 Service를 통해)
- UI 위젯 직접 생성 또는 조작
- 하드코딩된 설정값 사용
- 동기적 네트워크 또는 파일 I/O