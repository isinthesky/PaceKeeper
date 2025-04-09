"""
PaceKeeper Qt - 메인 윈도우
애플리케이션 메인 윈도우 리팩토링된 구현
"""

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSlot # pyqtSlot 임포트
from PyQt6.QtGui import QAction # QAction 임포트
from PyQt6.QtWidgets import QSplitter, QToolBar, QStatusBar, QMenuBar # QMenuBar 추가 임포트

from app.config.app_config import AppConfig
from app.controllers.main_controller import MainController
from app.controllers.timer_controller import TimerController
from app.domain.log.log_service import LogService
from app.domain.tag.tag_service import TagService
from app.domain.category.category_service import CategoryService
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.utils.constants import TimerState, SessionType # TimerState 임포트

# 리팩토링된 모듈 임포트
from app.views.main_window.ui_setup import setup_ui, setup_tray_icon
from app.views.main_window.event_handlers import ( # 사용하지 않는 핸들러 제거 예정
    on_session_started, on_session_paused, on_session_resumed,
    on_session_stopped, on_session_finished, on_text_submitted,
    on_tag_selected, on_log_selected, on_tray_icon_activated,
    on_exit_from_tray, close_event
)
from app.views.main_window.actions import (
    open_settings, open_log_dialog,
    open_category_dialog, open_tag_dialog, show_break_dialog,
    show_stats, show_help, show_about
)
from app.views.main_window.ui_updates import (
    update_ui, update_recent_logs, update_tags
)

from app.views.timer_widget_responsive import TimerWidget
from app.views.text_input_widget import TextInputWidget
from app.views.tag_widget import TagButtonsWidget
from app.views.log_widget import LogListWidget


class MainWindow(QMainWindow):
    """애플리케이션 메인 윈도우 클래스""" 
    
    # --- UI 요소 타입 힌트 --- 
    timerWidget: TimerWidget
    textInputWidget: TextInputWidget
    tagButtonsWidget: TagButtonsWidget
    logListWidget: LogListWidget
    contentSplitter: QSplitter
    toolBar: QToolBar
    statusBar: QStatusBar
    startStopAction: QAction
    pauseResumeAction: QAction
    trayStartStopAction: QAction
    trayPauseResumeAction: QAction
    # 필요한 다른 UI 요소 타입 힌트 추가 (예: menuBar)
    menuBar: QMenuBar

    # --- 컨트롤러 타입 힌트 --- 
    main_controller: MainController
    timer_controller: TimerController
    
    def __init__(self, app_config=None, theme_manager=None):
        """
        메인 윈도우 초기화
        
        Args:
            app_config: 애플리케이션 설정 관리자
            theme_manager: 테마 관리자
        """
        super().__init__()
        
        # 컴포넌트 초기화
        self.config = app_config or AppConfig()
        self.theme_manager = theme_manager or AdvancedThemeManager()
        
        # --- 서비스 초기화 제거 --- 
        
        # 컨트롤러 초기화 (서비스는 컨트롤러가 내부적으로 관리)
        self.timer_controller = TimerController()
        self.main_controller = MainController(
            app_config=self.config,
            timer_controller=self.timer_controller,
        )
        
        # UI 초기화 메서드 바인딩
        setup_ui(self) # setup_ui는 TimerWidget을 사용하도록 수정됨
        setup_tray_icon(self)
        
        # 이벤트 핸들러 메서드 바인딩 (사용하지 않는 것 제거)
        # self.onTimerStart = lambda: on_timer_start(self)
        # self.onTimerPause = lambda: on_timer_pause(self)
        # self.onTimerStateChanged = lambda state: on_timer_state_changed(self, state)
        self.onSessionStarted = lambda session_type: on_session_started(self, session_type)
        self.onSessionPaused = lambda: on_session_paused(self)
        self.onSessionResumed = lambda: on_session_resumed(self)
        self.onSessionStopped = lambda: on_session_stopped(self)
        self.onSessionFinished = lambda session_type: on_session_finished(self, session_type)
        self.onTextSubmitted = lambda text: on_text_submitted(self, text)
        self.onTagSelected = lambda tag_name: on_tag_selected(self, tag_name)
        self.onLogSelected = lambda log_text: on_log_selected(self, log_text)
        self.onTrayIconActivated = lambda reason: on_tray_icon_activated(self, reason)
        self.onExitFromTray = lambda: on_exit_from_tray(self)
        
        # 액션 메서드 바인딩 (사용하지 않는 것 제거)
        # self.toggleTimer = lambda: toggle_timer(self) # _handle_timer_toggle_request 로 대체
        # self.togglePause = lambda: toggle_pause(self) # _handle_timer_pause_toggle_request 로 대체
        self.openSettings = lambda: open_settings(self)
        self.openLogDialog = lambda: open_log_dialog(self)
        self.openCategoryDialog = lambda: open_category_dialog(self)
        self.openTagDialog = lambda: open_tag_dialog(self)
        self.showBreakDialog = lambda session_type: show_break_dialog(self, session_type)
        self.showStats = lambda: show_stats(self)
        self.showHelp = lambda: show_help(self)
        self.showAbout = lambda: show_about(self)
        
        # UI 업데이트 메서드 바인딩 (사용하지 않는 것 제거)
        self.updateUI = lambda: update_ui(self)
        self.updateRecentLogs = lambda: update_recent_logs(self)
        self.updateTags = lambda: update_tags(self)
        # self.updateTimerDisplay = lambda timeStr: update_timer_display(self, timeStr) # _update_timer_ui_state 로 대체
        
        # 시그널 연결 (connect_signals 함수 대신 여기서 직접 연결)
        # connect_signals(self) 제거

        # -- 새로운 시그널 연결 --
        # TimerWidget 시그널 -> 핸들러
        self.timerWidget.startRequested.connect(self._handle_timer_toggle_request)
        self.timerWidget.pauseRequested.connect(self._handle_timer_pause_toggle_request)

        # 툴바 액션 시그널 -> 핸들러
        self.startStopAction.triggered.connect(self._handle_timer_toggle_request)
        self.pauseResumeAction.triggered.connect(self._handle_timer_pause_toggle_request)

        # 트레이 액션 시그널 -> 핸들러
        self.trayStartStopAction.triggered.connect(self._handle_timer_toggle_request)
        self.trayPauseResumeAction.triggered.connect(self._handle_timer_pause_toggle_request)

        # 컨트롤러 시그널 -> 슬롯
        self.timer_controller.timerStateChanged.connect(self._update_timer_ui_state)
        self.main_controller.sessionStarted.connect(self.onSessionStarted) # 기존 핸들러 유지
        self.main_controller.sessionPaused.connect(self.onSessionPaused)
        self.main_controller.sessionResumed.connect(self.onSessionResumed)
        self.main_controller.sessionStopped.connect(self.onSessionStopped)
        self.main_controller.sessionFinished.connect(self.onSessionFinished)
        self.main_controller.logCreated.connect(self.updateRecentLogs) # 로그 생성 시 UI 업데이트
        # self.main_controller.tagsLoaded.connect(self.updateTags) # 필요시 연결
        # self.main_controller.categoriesLoaded.connect(...) # 필요시 연결

        # TextInputWidget 시그널 연결 (기존 connect_signals에 있었다면 여기에 추가)
        self.textInputWidget.textSubmitted.connect(self.onTextSubmitted)
        # self.textInputWidget.tagPatternDetected.connect(self.onTagSelected) # 시그널 정의 확인 필요, 주석 처리

        # TagButtonsWidget 시그널 연결 (기존 connect_signals에 있었다면 여기에 추가)
        self.tagButtonsWidget.tagSelected.connect(self.onTagSelected)

        # LogListWidget 시그널 연결 (기존 connect_signals에 있었다면 여기에 추가)
        self.logListWidget.logSelected.connect(self.onLogSelected)
        # -- 시그널 연결 끝 --
        
        # 초기 상태 설정
        self.updateUI() # 테마 등 초기 UI 설정
        self.updateRecentLogs() # 초기 로그 로드
        self.updateTags() # 초기 태그 로드
        # 초기 타이머 상태 설정 (컨트롤러에서 초기 상태 시그널을 보내도록 하는 것이 좋음)
        initial_state = self.timer_controller.get_state()
        initial_time = self.timer_controller._get_formatted_time_str(self.timer_controller.get_remaining_time())
        self._update_timer_ui_state(initial_state, initial_time)
    
    def closeEvent(self, event):
        """
        창 닫기 이벤트 처리
        
        Args:
            event: 닫기 이벤트
        """
        close_event(self, event)
        
    # --- toggleTimer, togglePause 메서드 제거 --- 
        
    def openSettings(self):
        """
        설정 대화상자 열기
        바인딩된 함수가 제대로 작동하지 않을 경우를 대비한 직접 구현
        """
        from app.views.dialogs.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self, self.config, self.theme_manager)
        result = settings_dialog.exec()
        if result:
            # 설정이 변경되면 UI 업데이트
            self.updateUI()
            
    def openLogDialog(self):
        """로그 대화상자 열기"""
        from app.views.dialogs.log_dialog import LogDialog
        # 서비스 대신 컨트롤러 전달 (LogDialog 수정 필요)
        log_dialog = LogDialog(self, self.main_controller)
        log_dialog.exec()
        
        # 대화상자가 닫힌 후 최근 로그 업데이트 - 컨트롤러 시그널로 처리됨
        # self.updateRecentLogs() 제거
        
    def openCategoryDialog(self):
        """카테고리 대화상자 열기"""
        from app.views.dialogs.category_dialog import CategoryDialog
        # 서비스 대신 컨트롤러 전달 (CategoryDialog 수정 필요)
        category_dialog = CategoryDialog(self, self.main_controller)
        category_dialog.exec()
        
    def openTagDialog(self):
        """태그 대화상자 열기"""
        from app.views.dialogs.tag_dialog import TagDialog
        # 서비스 대신 컨트롤러 전달 (TagDialog 수정 필요)
        tag_dialog = TagDialog(self, self.main_controller)
        tag_dialog.exec()
        
        # 대화상자가 닫힌 후 태그 목록 업데이트 - 컨트롤러 시그널로 처리됨
        # self.updateTags() 제거
        
    def showBreakDialog(self, session_type):
        """
        휴식 대화상자 표시
        
        Args:
            session_type: 세션 타입 (SHORT_BREAK 또는 LONG_BREAK)
        """
        from app.views.dialogs.break_dialog import BreakDialog
        from app.utils.constants import SessionType
        
        break_dialog = BreakDialog(self, session_type)
        
        # 휴식 시작 시그널 연결
        break_dialog.startBreakRequested.connect(
            lambda: self.main_controller.start_session(session_type)
        )
        
        # 휴식 건너뛰기 시그널 연결
        break_dialog.skipBreakRequested.connect(
            lambda: self.main_controller.start_session(SessionType.POMODORO)
        )
        
        # 대화상자 표시
        break_dialog.exec()
        
    def showStats(self):
        """통계 보기"""
        from PyQt6.QtWidgets import QMessageBox
        # 실제 구현에서는 통계 대화상자 생성 및 표시
        QMessageBox.information(self, "통계", "통계 기능은 개발 중입니다.")
        
    def showHelp(self):
        """도움말 표시"""
        from PyQt6.QtWidgets import QMessageBox
        help_text = """
        <h3>PaceKeeper 사용법</h3>
        <p>
        <b>기본 사용:</b>
        <ul>
            <li>시작 버튼을 눌러 뽀모도로 세션을 시작합니다.</li>
            <li>일시정지 버튼으로 필요시 타이머를 일시정지할 수 있습니다.</li>
            <li>중지 버튼으로 세션을 완전히 중단할 수 있습니다.</li>
            <li>세션이 끝나면 자동으로 휴식 시간이 시작됩니다.</li>
        </ul>
        </p>
        <p>
        <b>로그 및 태그:</b>
        <ul>
            <li>텍스트 입력 필드에 작업 내용을 기록하세요.</li>
            <li>#태그 형식으로 태그를 추가할 수 있습니다.</li>
            <li>태그 버튼을 클릭하여 자주 사용하는 태그를 빠르게 추가할 수 있습니다.</li>
        </ul>
        </p>
        <p>
        <b>반응형 레이아웃:</b>
        <ul>
            <li>창 크기에 따라 자동으로 레이아웃이 조정됩니다.</li>
            <li>작은 화면에서는 세로 레이아웃, 넓은 화면에서는 가로 레이아웃으로 전환됩니다.</li>
            <li>보기 메뉴에서 수동으로 레이아웃을 전환할 수 있습니다.</li>
        </ul>
        </p>
        """
        QMessageBox.information(self, "PaceKeeper 도움말", help_text)
        
    def showAbout(self):
        """정보 대화상자 표시"""
        from PyQt6.QtWidgets import QMessageBox
        about_text = """
        <h3>PaceKeeper</h3>
        <p>버전: 2.0.0</p>
        <p>간단하고 효과적인 시간 관리 도구</p>
        <p>© 2023 PaceKeeper Team</p>
        <p>Qt 프레임워크 기반 마이그레이션 완료 버전</p>
        """
        QMessageBox.about(self, "PaceKeeper 정보", about_text)
        
    def onExitFromTray(self):
        """트레이에서 종료 액션 핸들러"""
        self.close()
        
    def onTrayIconActivated(self, reason):
        """
        트레이 아이콘 활성화 핸들러
        
        Args:
            reason: 활성화 이유
        """
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 더블 클릭 시 창 보이기
            self.showNormal()
            self.activateWindow()

    # --- updateTimerDisplay 메서드 제거 ---
            
    def _restore_normal_ui(self):
        """일반 모드 UI로 복원"""
        # 미니 버튼 컨테이너 숨기기 - TimerWidget으로 대체되었으므로 관련 로직 수정/제거 필요
        # self.miniButtonContainer.hide()
        
        # 일반 UI 요소 복원
        self.contentSplitter.show()
        self.menuBar.show()
        self.toolBar.show()
        self.statusBar.show()
        
        # 창 크기 복원
        self.setFixedSize(16777215, 16777215)  # 고정 크기 제거 (QWIDGETSIZE_MAX)
        self.resize(
            self.config.get("main_dlg_width", 800),
            self.config.get("main_dlg_height", 500)
        )

    # --- 새로운 핸들러 및 슬롯 메서드 --- 
    @pyqtSlot()
    def _handle_timer_toggle_request(self):
        """TimerWidget 또는 툴바/트레이의 시작/중지 요청 처리"""
        current_state = self.timer_controller.get_state()
        
        if current_state in [TimerState.IDLE, TimerState.FINISHED]:
            current_text = self.textInputWidget.text()
            # 컨트롤러에 시작 요청 (메시지 전달)
            self.main_controller.start_session(message=current_text)
            # 입력 필드 비우기
            self.textInputWidget.clear()
        else: # RUNNING, PAUSED, BREAK 상태
            # 컨트롤러에 중지 요청
            self.main_controller.stop_session()

    @pyqtSlot()
    def _handle_timer_pause_toggle_request(self):
        """TimerWidget 또는 툴바/트레이의 일시정지/재개 요청 처리"""
        # 컨트롤러에 토글 요청
        self.main_controller.toggle_pause()

    @pyqtSlot(TimerState, str)
    def _update_timer_ui_state(self, state: TimerState, time_str: str):
        """타이머 상태 변경 시 UI 업데이트 슬롯"""
        # 1. TimerWidget 업데이트
        self.timerWidget.setTimerState(state, time_str)

        # 2. 툴바 액션 업데이트
        if state == TimerState.RUNNING:
            self.startStopAction.setText("중지")
            self.startStopAction.setEnabled(True)
            self.pauseResumeAction.setText("일시정지")
            self.pauseResumeAction.setEnabled(True)
        elif state == TimerState.PAUSED:
            self.startStopAction.setText("중지") # 중지 가능
            self.startStopAction.setEnabled(True)
            self.pauseResumeAction.setText("재개")
            self.pauseResumeAction.setEnabled(True)
        elif state in [TimerState.IDLE, TimerState.FINISHED, TimerState.BREAK]: # BREAK 상태 처리 추가 필요 시
            self.startStopAction.setText("시작")
            self.startStopAction.setEnabled(True)
            self.pauseResumeAction.setText("일시정지")
            self.pauseResumeAction.setEnabled(False)
        # 필요시 다른 상태에 대한 처리 추가

        # 3. 트레이 액션 업데이트
        if state == TimerState.RUNNING:
            self.trayStartStopAction.setText("중지")
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("일시정지")
            self.trayPauseResumeAction.setEnabled(True)
        elif state == TimerState.PAUSED:
            self.trayStartStopAction.setText("중지") # 중지 가능
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("재개")
            self.trayPauseResumeAction.setEnabled(True)
        elif state in [TimerState.IDLE, TimerState.FINISHED, TimerState.BREAK]: # BREAK 상태 처리 추가 필요 시
            self.trayStartStopAction.setText("시작")
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("일시정지")
            self.trayPauseResumeAction.setEnabled(False)
        # 필요시 다른 상태에 대한 처리 추가

        # 4. 상태바 업데이트 (선택 사항)
        # self.statusLabel.setText(f"상태: {state.name}, 시간: {time_str}")
