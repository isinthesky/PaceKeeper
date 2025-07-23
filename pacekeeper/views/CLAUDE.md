# Views Layer - CLAUDE.md

## 레이어 개요
Views 레이어는 사용자 인터페이스를 담당하며, PyQt5를 사용한 데스크톱 애플리케이션의 UI 컴포넌트들을 포함합니다.

## 담당 임무

### 핵심 책임
- **사용자 인터페이스**: 윈도우, 다이얼로그, 컨트롤 등 UI 요소 구현
- **이벤트 수집**: 사용자 입력과 상호작용 이벤트 캡처
- **데이터 표시**: Controller로부터 받은 데이터를 사용자에게 시각적으로 표현
- **사용성**: 직관적이고 반응성이 좋은 사용자 경험 제공

### 주요 컴포넌트별 역할
- **main_window.py**: 애플리케이션의 메인 윈도우, 전체 레이아웃 관리
- **main_frame.py**: 타이머 및 주요 컨트롤이 위치한 메인 프레임
- **controls.py**: 버튼, 입력 필드 등 재사용 가능한 UI 컨트롤
- **break_dialog.py**: 휴식 시간 알림 및 선택 다이얼로그
- **log_dialog.py**: 작업 로그 조회 및 관리 다이얼로그
- **category_dialog.py**: 카테고리 생성 및 편집 다이얼로그
- **settings_dialog.py**: 애플리케이션 설정 다이얼로그

## 코드 작성 규칙

### 아키텍처 패턴
- **MVP 패턴**: View는 순수한 UI 로직만 담당, 비즈니스 로직은 Controller에게 위임
- **시그널/슬롯**: PyQt5의 시그널/슬롯 메커니즘을 통한 이벤트 처리
- **컴포넌트 분리**: 재사용 가능한 UI 컴포넌트로 분해

### 네이밍 컨벤션
```python
# 클래스명: PascalCase, UI 요소 타입 접미사
class MainWindow(QMainWindow):
class BreakDialog(QDialog):
class TimerControl(QWidget):

# 위젯 변수명: snake_case + 타입 접미사
self.start_button = QPushButton()
self.timer_label = QLabel()
self.category_combo = QComboBox()

# 시그널명: snake_case + _signal 접미사
timer_started_signal = pyqtSignal()
settings_changed_signal = pyqtSignal(str, object)

# 슬롯 메서드: on_ 접두사 + 위젯명 + 이벤트
def on_start_button_clicked(self) -> None:
def on_category_combo_changed(self, text: str) -> None:
```

### UI 초기화 패턴
```python
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        self.apply_styles()
    
    def setup_ui(self) -> None:
        """UI 요소 생성 및 레이아웃 설정"""
        self.setWindowTitle(Labels.get_label("app_title"))
        self.setMinimumSize(400, 300)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 생성
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.create_timer_section())
        layout.addWidget(self.create_control_section())
    
    def connect_signals(self) -> None:
        """시그널과 슬롯 연결"""
        self.start_button.clicked.connect(self.on_start_clicked)
    
    def apply_styles(self) -> None:
        """스타일시트 적용"""
        self.setStyleSheet(self.load_stylesheet())
```

### 다국어 지원 패턴
```python
# 모든 텍스트는 Labels.get_label() 사용
self.start_button.setText(Labels.get_label("start_timer"))
self.setWindowTitle(Labels.get_label("main_window_title"))

# 동적 언어 변경 지원
def retranslate_ui(self) -> None:
    self.start_button.setText(Labels.get_label("start_timer"))
    self.stop_button.setText(Labels.get_label("stop_timer"))
```

### 이벤트 처리 패턴
```python
# 사용자 액션은 시그널로 전달
def on_start_button_clicked(self) -> None:
    category = self.category_combo.currentText()
    tags = self.tags_input.text().split(',')
    self.timer_start_requested.emit(category, tags)

# Controller로부터 상태 업데이트 수신
def update_timer_display(self, remaining_seconds: int) -> None:
    minutes, seconds = divmod(remaining_seconds, 60)
    self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

def show_break_notification(self, break_type: str) -> None:
    self.break_dialog.show_break(break_type)
```

### 에러 처리 및 사용자 피드백
```python
def show_error(self, message: str) -> None:
    QMessageBox.critical(self, Labels.get_label("error"), message)

def show_warning(self, message: str) -> None:
    QMessageBox.warning(self, Labels.get_label("warning"), message)

def show_info(self, message: str) -> None:
    QMessageBox.information(self, Labels.get_label("info"), message)
```

### 리소스 관리
```python
def closeEvent(self, event: QCloseEvent) -> None:
    """윈도우 종료 시 리소스 정리"""
    self.save_window_state()
    if hasattr(self, 'timer'):
        self.timer.stop()
    event.accept()

def load_stylesheet(self) -> str:
    """스타일시트 파일 로드"""
    style_path = resource_path("assets/styles/main.qss")
    with open(style_path, 'r', encoding='utf-8') as f:
        return f.read()
```

### 성능 고려사항
- **지연 로딩**: 복잡한 다이얼로그는 필요시에만 생성
- **이벤트 최적화**: 빈번한 업데이트는 타이머나 스레드 활용
- **메모리 관리**: 위젯 참조 해제 및 시그널 연결 해제

### 금지사항
- 비즈니스 로직이나 데이터 처리 로직 포함
- 직접적인 데이터베이스 접근
- Service나 Repository 직접 호출
- 하드코딩된 텍스트 (다국어 지원 위반)