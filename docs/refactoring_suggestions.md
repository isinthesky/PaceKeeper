# PaceKeeper 리팩토링 제안사항

## 개요

PaceKeeper는 잘 구조화된 MVC 아키텍처를 기반으로 하는 뽀모도로 시간 관리 애플리케이션입니다. 이 문서는 프로젝트의 품질, 유지보수성, 확장성을 더욱 향상시키기 위한 리팩토링 제안사항을 제시합니다.

## 1. 테스트 코드 강화

### 현재 상태
- 현재 프로젝트에는 tests/ 디렉토리가 존재하지만 실질적인 테스트 코드가 부족합니다.
- 단위 테스트, 통합 테스트, UI 테스트 등이 체계적으로 구현되어 있지 않습니다.

### 개선 방안

#### 1.1 테스트 프레임워크 도입
```python
# pyproject.toml에 테스트 의존성 추가
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-qt = "^4.2.0"
pytest-cov = "^4.1.0"
```

#### 1.2 단위 테스트 구현
레포지토리, 서비스, 컨트롤러 레이어별 단위 테스트를 작성합니다.

```python
# tests/services/test_log_service.py 예시
import pytest
from unittest.mock import MagicMock, patch
from pacekeeper.services.log_service import LogService
from pacekeeper.repository.entities import Log

def test_create_study_log():
    # Arrange
    mock_repository = MagicMock()
    log_service = LogService()
    log_service._log_repository = mock_repository
    
    # Act
    log_service.create_study_log("테스트 작업 #태그1 #태그2")
    
    # Assert
    mock_repository.add.assert_called_once()
    args, _ = mock_repository.add.call_args
    log = args[0]
    assert isinstance(log, Log)
    assert log.message == "테스트 작업 #태그1 #태그2"
    assert "태그1" in log.tags
    assert "태그2" in log.tags
```

#### 1.3 통합 테스트 구현
여러 컴포넌트가 함께 작동하는 기능에 대한 통합 테스트를 작성합니다.

```python
# tests/integration/test_timer_workflow.py 예시
import pytest
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.controllers.config_controller import ConfigController, AppStatus

def test_timer_cycle_progression(qtbot):
    # 실제 컴포넌트를 사용한 타이머 워크플로우 테스트
    config_ctrl = ConfigController()
    # MainWindow 모킹 또는 실제 객체 생성
    main_window = create_test_main_window()
    
    controller = MainController(main_window, config_ctrl)
    
    # 타이머 시작
    controller.start_study_session()
    assert config_ctrl.get_status() == AppStatus.STUDY
    
    # 타이머 완료 시뮬레이션
    controller.on_study_session_finished()
    
    # 첫 번째 사이클 후에는 짧은 휴식으로 전환되어야 함
    assert config_ctrl.get_status() == AppStatus.SHORT_BREAK
    assert config_ctrl.get_cycle() == 1
```

#### 1.4 UI 테스트 구현
PyQt 컴포넌트 및 상호작용에 대한 테스트를 작성합니다.

```python
# tests/views/test_settings_dialog.py 예시
import pytest
from PyQt5.QtCore import Qt
from pacekeeper.views.settings_dialog import SettingsDialog
from pacekeeper.controllers.config_controller import ConfigController

def test_settings_dialog_save(qtbot):
    # 설정 다이얼로그 테스트
    config = ConfigController()
    dialog = SettingsDialog(None, config)
    qtbot.addWidget(dialog)
    
    # 설정값 변경
    study_time_input = dialog.findChild(QSpinBox, "studyTimeInput")
    qtbot.set_spin_value(study_time_input, 30)
    
    # 저장 버튼 클릭
    save_button = dialog.findChild(QPushButton, "saveButton")
    qtbot.mouseClick(save_button, Qt.LeftButton)
    
    # 설정이 저장되었는지 확인
    assert config.get_setting("study_time") == 30
```

#### 1.5 테스트 자동화
CI/CD 파이프라인에 테스트 자동화를 추가합니다.

```yaml
# .github/workflows/tests.yml 예시
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install poetry
          poetry install
      - name: Run tests
        run: |
          poetry run pytest --cov=pacekeeper
```

## 2. 타입 힌트 및 문서화 강화

### 현재 상태
- 일부 코드에만 타입 힌트가 적용되어 있으며, 문서화가 불균일합니다.
- 한국어 주석이 혼합되어 있어 국제적 협업에 제한이 있습니다.

### 개선 방안

#### 2.1 타입 힌트 일관적 적용
모든 함수와 메서드에 타입 힌트를 추가합니다.

```python
# 개선 전
def create_study_log(self, message, study_start_time=None):
    # 구현 내용

# 개선 후
from datetime import datetime
from typing import Optional

def create_study_log(self, message: str, study_start_time: Optional[datetime] = None) -> int:
    """작업 로그를 생성하고 저장합니다.
    
    Args:
        message: 로그 메시지 (태그 포함 가능)
        study_start_time: 학습 시작 시간 (기본값: 현재 시간)
        
    Returns:
        생성된 로그의 ID
    
    Raises:
        ValueError: 메시지가 비어있을 경우
    """
    # 구현 내용
```

#### 2.2 타입 검사 도구 도입
mypy를 도입하여 정적 타입 검사를 수행합니다.

```python
# pyproject.toml에 추가
[tool.poetry.group.dev.dependencies]
mypy = "^1.4.1"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

#### 2.3 문서화 표준화
모든 모듈, 클래스, 메서드에 일관된 docstring 형식을 적용합니다.

```python
# 모듈 문서화 예시
"""
카테고리 관리 서비스 모듈

이 모듈은 카테고리 엔티티에 대한 생성, 조회, 수정, 삭제 기능을 제공합니다.
"""

# 클래스 문서화 예시
class CategoryService:
    """
    카테고리 관리 서비스
    
    카테고리 엔티티에 대한 비즈니스 로직을 처리하고,
    레포지토리 레이어와 컨트롤러 레이어 사이의 인터페이스 역할을 합니다.
    """
```

#### 2.4 주석의 이중 언어 지원 또는 영어 통일
공개 API 및 중요 로직에 대해 영어 주석을 추가하거나 모든 주석을 영어로 통일합니다.

```python
# 이중 언어 주석 예시
def on_study_session_finished(self):
    """학습 세션 종료 후 실행될 로직 및 휴식 세션 전환
    
    Executes logic after study session finishes and transitions to break session.
    """
```

## 3. 설정 및 상태 관리 개선

### 현재 상태
- ConfigController가 싱글톤으로 구현되어 있어 테스트 어려움과 결합도 증가 문제가 있습니다.
- 애플리케이션 상태(AppStatus)와 설정이 하나의 컨트롤러에 혼합되어 있습니다.

### 개선 방안

#### 3.1 의존성 주입 패턴 적용
싱글톤 대신 의존성 주입 패턴을 사용하여 테스트 용이성과 결합도를 개선합니다.

```python
# 개선 전
class SomeController:
    def __init__(self):
        self.config = ConfigController()  # 싱글톤 직접 참조

# 개선 후
class SomeController:
    def __init__(self, config_controller):
        self.config = config_controller  # 의존성 주입
```

#### 3.2 상태 관리 분리
애플리케이션 상태와 설정 관리를 분리합니다.

```python
# config_controller.py를 분리
class SettingsManager:
    """설정 로드, 저장, 접근 관련 기능만 담당"""
    def __init__(self, config_file):
        self.config_file = config_file
        self.settings = self._load_settings()
    
    # 설정 관련 메서드들...

class AppStateManager:
    """애플리케이션 상태 관리만 담당"""
    def __init__(self):
        self._status = AppStatus.IDLE
        self._cycle = 0
    
    # 상태 관련 메서드들...
```

#### 3.3 Observable 패턴 도입
설정 및 상태 변경 시 옵저버에게 알림을 주는 패턴을 적용합니다.

```python
class Observable:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        self._observers.remove(observer)
    
    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(*args, **kwargs)

class AppStateManager(Observable):
    def __init__(self):
        super().__init__()
        self._status = AppStatus.IDLE
    
    def set_status(self, status):
        old_status = self._status
        self._status = status
        self.notify_observers("status_changed", old=old_status, new=status)
```

#### 3.4 설정 유효성 검사 강화
사용자 설정 데이터에 대한 유효성 검사를 강화합니다.

```python
def update_settings(self, new_settings):
    """설정 업데이트 전 유효성 검사 수행"""
    errors = []
    
    # 학습 시간 검증
    if "study_time" in new_settings:
        study_time = new_settings["study_time"]
        if not isinstance(study_time, int) or study_time < 1 or study_time > 120:
            errors.append("학습 시간은 1~120 사이의 정수여야 합니다.")
    
    # 다른 설정들 검증...
    
    if errors:
        raise ValueError("\n".join(errors))
    
    # 유효성 검사를 통과한 경우에만 설정 업데이트
    self.settings.update(new_settings)
    self._save_settings()
```

## 결론

위에서 제안한 세 가지 리팩토링 영역(테스트 코드 강화, 타입 힌트 및 문서화 강화, 설정 및 상태 관리 개선)은 PaceKeeper 프로젝트의 다음과 같은 측면을 향상시킬 것입니다:

1. **품질 향상**: 자동화된 테스트를 통해 버그를 조기에 발견하고 코드 품질 향상
2. **유지보수성 개선**: 명확한 타입 힌트와 문서화로 코드 이해 및 유지보수 용이성 증가
3. **확장성 강화**: 관심사 분리를 통한 모듈화 개선 및 확장 가능성 증대
4. **협업 용이성**: 표준화된 문서화와 테스트로 새로운 개발자의 온보딩 과정 간소화

이러한 리팩토링은 단계적으로 진행할 수 있으며, 각 단계별로 코드 품질과 개발 경험을 점진적으로 향상시킬 수 있습니다. 프로젝트의 현재 성숙도와 향후 발전 방향을 고려할 때, 이러한 개선사항들은 PaceKeeper의 장기적인 성공과 지속 가능성에 크게 기여할 것입니다.