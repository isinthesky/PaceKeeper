from icecream import ic
from PyQt6.QtCore import pyqtSlot, QTimer  # pyqtSlot 임포트
from PyQt6.QtGui import QAction  # QAction 임포트
from PyQt6.QtWidgets import QMenuBar  # QMenuBar 추가 임포트
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QStatusBar,
                             QToolBar)

from app.config.app_config import AppConfig
from app.controllers.main_controller import MainController
from app.controllers.timer_controller import TimerController
from app.utils.constants import TimerState  # TimerState 임포트
from app.views.log_widget import LogListWidget
from app.views.main_window.actions import (open_category_dialog,
                                           open_log_dialog, open_settings,
                                           open_tag_dialog, show_about,
                                           show_break_dialog, show_help,
                                           show_stats)
from app.views.main_window.event_handlers import (  # 사용하지 않는 핸들러 제거 예정
    close_event, on_exit_from_tray, on_log_selected, on_session_finished,
    on_session_paused, on_session_resumed, on_session_started,
    on_session_stopped, on_tag_selected, on_text_submitted,
    on_tray_icon_activated)
# 리팩토링된 모듈 임포트
from app.views.main_window.ui_setup import setup_tray_icon, setup_ui
from app.views.main_window.ui_updates import (update_recent_logs, update_tags,
                                              update_ui)
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.tag_widget import TagButtonsWidget
from app.views.text_input_widget import TextInputWidget
from app.views.timer_widget_responsive import TimerWidget


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

    def __init__(self, app_config=None, theme_manager=None, app_instance=None):
        """
        메인 윈도우 초기화

        Args:
            app_config: 애플리케이션 설정 관리자
            theme_manager: 테마 관리자
            app_instance: QApplication 인스턴스 (테마 변경 시 사용)
        """
        super().__init__()

        # QApplication 인스턴스 저장
        self.app_instance = app_instance or QApplication.instance()

        # 컴포넌트 초기화
        self.config = app_config or AppConfig()
        # 단일 테마 관리자 인스턴스 사용
        self.theme_manager = theme_manager or AdvancedThemeManager.get_instance(
            app=self.app_instance
        )

        # 테마 관리자에 메인 윈도우 등록 및 시그널 연결
        if self.theme_manager:
            self.theme_manager.register_widget(self)
            # 테마 변경 시그널 연결
            self.theme_manager.themeChanged.connect(self.on_theme_changed)

        # --- 서비스 초기화 제거 ---

        # 컨트롤러 초기화 (서비스는 컨트롤러가 내부적으로 관리)
        self.timer_controller = TimerController()
        self.main_controller = MainController(
            app_config=self.config,
            timer_controller=self.timer_controller,
        )

        # UI 초기화 메서드 바인딩
        setup_ui(self)  # setup_ui는 TimerWidget을 사용하도록 수정됨
        setup_tray_icon(self)

        # 이벤트 핸들러 메서드 바인딩 (사용하지 않는 것 제거)
        # self.onTimerStart = lambda: on_timer_start(self)
        # self.onTimerPause = lambda: on_timer_pause(self)
        # self.onTimerStateChanged = lambda state: on_timer_state_changed(self, state)
        self.onSessionStarted = lambda session_type: on_session_started(
            self, session_type
        )
        self.onSessionPaused = lambda: on_session_paused(self)
        self.onSessionResumed = lambda: on_session_resumed(self)
        self.onSessionStopped = lambda: on_session_stopped(self)
        self.onSessionFinished = lambda session_type: on_session_finished(
            self, session_type
        )
        self.onTextSubmitted = lambda text: on_text_submitted(self, text)
        self.onTagSelected = lambda tag_name: on_tag_selected(self, tag_name)
        self.onLogSelected = lambda log_text: on_log_selected(self, log_text)
        self.onTrayIconActivated = lambda reason: on_tray_icon_activated(self, reason)
        self.onExitFromTray = lambda: on_exit_from_tray(self)

        # 이름 변경: 함수 이름과 메서드 이름을 동일하게 설정
        self.open_settings = lambda: open_settings(self)
        self.open_log_dialog = lambda: open_log_dialog(self)
        self.open_category_dialog = lambda: open_category_dialog(self)
        self.open_tag_dialog = lambda: open_tag_dialog(self)
        self.show_break_dialog = lambda session_type: show_break_dialog(
            self, session_type
        )
        self.show_stats = lambda: show_stats(self)
        self.show_help = lambda: show_help(self)
        self.show_about = lambda: show_about(self)
        
        # actions.py에서 이동한 메서드 바인딩
        from app.views.main_window.actions import on_settings_changed
        self.on_settings_changed = lambda settings: on_settings_changed(self, settings)

        # UI 업데이트 메서드 바인딩 (사용하지 않는 것 제거)
        self.updateUI = lambda: update_ui(self)
        self.updateRecentLogs = lambda: update_recent_logs(self)
        self.updateTags = lambda: update_tags(self)

        # -- 새로운 시그널 연결 --
        # TimerWidget 시그널 -> 핸들러
        self.timerWidget.startRequested.connect(self._handle_timer_toggle_request)
        self.timerWidget.pauseRequested.connect(self._handle_timer_pause_toggle_request)

        # 툴바 액션 시그널 -> 핸들러
        self.startStopAction.triggered.connect(self._handle_timer_toggle_request)
        self.pauseResumeAction.triggered.connect(
            self._handle_timer_pause_toggle_request
        )

        # 트레이 액션 시그널 -> 핸들러
        self.trayStartStopAction.triggered.connect(self._handle_timer_toggle_request)
        self.trayPauseResumeAction.triggered.connect(
            self._handle_timer_pause_toggle_request
        )

        # 컨트롤러 시그널 -> 슬롯
        self.timer_controller.timerStateChanged.connect(self._update_timer_ui_state)
        self.main_controller.sessionStarted.connect(
            self.onSessionStarted
        )  # 기존 핸들러 유지
        self.main_controller.sessionPaused.connect(self.onSessionPaused)
        self.main_controller.sessionResumed.connect(self.onSessionResumed)
        self.main_controller.sessionStopped.connect(self.onSessionStopped)
        self.main_controller.sessionFinished.connect(self.onSessionFinished)
        self.main_controller.logCreated.connect(
            self.updateRecentLogs
        )

        self.textInputWidget.textSubmitted.connect(self.onTextSubmitted)

        self.tagButtonsWidget.tagSelected.connect(self.onTagSelected)

        self.logListWidget.logSelected.connect(self.onLogSelected)
        # -- 시그널 연결 끝 --

        # 초기 상태 설정
        self.updateRecentLogs()  # 초기 로그 로드
        self.updateTags()  # 초기 태그 로드

        # 초기 타이머 상태 설정 (컨트롤러에서 초기 상태 시그널을 보내도록 하는 것이 좋음)
        initial_state = self.timer_controller.get_state()
        initial_time = self.timer_controller._get_formatted_time_str(
            self.timer_controller.get_remaining_time()
        )
        self._update_timer_ui_state(initial_state, initial_time)

        # 테마 업데이트 메서드 호출
        QTimer.singleShot(0, self.updateUI)

    def closeEvent(self, event):
        """
        창 닫기 이벤트 처리

        Args:
            event: 닫기 이벤트
        """
        close_event(self, event)

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
            self.config.get("main_dlg_height", 500),
        )

    # --- 테마 변경 슬롯 추가 ---
    @pyqtSlot(str)
    def on_theme_changed(self, theme_name: str):
        """테마 변경 시그널을 처리하는 슬롯"""
        # 현재 테마를 설정에 저장 (중요!)
        self.config.set("theme", theme_name)

        # 애플리케이션 인스턴스 찾기
        app = self.app_instance  # 생성자에서 전달받은 인스턴스 우선 사용
        if app is None:
            # 전달받은 인스턴스가 없으면 싱글톤 인스턴스 사용 시도
            app = QApplication.instance()

        if app is None:
            # QApplication이 None인 경우 현재 위젯에만 적용
            print(
                "QApplication 인스턴스를 찾을 수 없습니다. 테마 변경이 일부만 적용될 수 있습니다."
            )
            style_content = self.theme_manager.get_theme_style(theme_name)
            if style_content:
                self.setStyleSheet(style_content)
        else:
            # 현재 테마를 가져와 필요한 작업 수행
            style_content = self.theme_manager.get_theme_style(theme_name)
            if style_content:
                self.setStyleSheet(style_content)

            # UI 업데이트 - 중요한 부분만 업데이트하여 성능 최적화
            self.updateRecentLogs()  # 로그 목록 새로고침
            self.updateTags()  # 태그 버튼 새로고침

    def change_theme(self, theme_name):
        """테마 변경 메서드 - 사용자가 테마를 직접 변경할 때 호출"""
        # 먼저 설정에 테마 이름 저장
        self.config.set("theme", theme_name)
        self.config.save_settings()

        # 테마 관리자에 애플리케이션 인스턴스 설정
        app = self.app_instance
        if app is None:
            app = QApplication.instance()
            if app is not None:
                self.app_instance = app  # 찾은 인스턴스 저장

        print(f"[DEBUG] 인스턴스 상태: app={app}, 유형={type(app) if app else 'None'}")

        if app is not None:
            # 테마 관리자에 액세스 여부 확인
            if self.theme_manager is None:
                print(f"[DEBUG] 경고: 테마 관리자가 None입니다!")
                self.theme_manager = AdvancedThemeManager.get_instance(app=app)

            # QApplication 인스턴스 명시적 설정
            self.theme_manager.set_application(app)

            # 테마 적용 (직접 인스턴스 전달)
            print(f"[DEBUG] 전체 애플리케이션에 테마 적용 시도: {theme_name}")
            result = self.theme_manager.apply_theme(target=app, theme_name=theme_name)
            print(f"[DEBUG] 테마 적용 결과: {result}")
        else:
            print(f"[DEBUG] 경고: 어떤 QApplication 인스턴스도 찾을 수 없습니다!")
            # 인스턴스 없이 적용 시도 (마지막 수단)
            result = self.theme_manager.apply_theme(theme_name=theme_name)

        # 현재 위젯에도 직접 테마 적용 (즉시 표시를 위해)
        style_content = self.theme_manager.get_theme_style(theme_name)
        if style_content:
            self.setStyleSheet(style_content)

        # UI 업데이트 - 위젯 유효성 검사 추가
        # 로그 목록 위젯 갱신
        if hasattr(self, "logListWidget"):
            try:
                # 객체가 유효한지 확인
                self.logListWidget.objectName()  # 존재하는 메서드 호출 시도
                self.updateRecentLogs()
            except RuntimeError:
                # 소멸된 위젯 - 무시
                pass

        # 태그 버튼 위젯 갱신
        if hasattr(self, "tagButtonsWidget"):
            try:
                # 객체가 유효한지 확인
                self.tagButtonsWidget.objectName()
                self.updateTags()
            except RuntimeError:
                # 소멸된 위젯 - 무시
                pass

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
        else:  # RUNNING, PAUSED, BREAK 상태
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
            self.startStopAction.setText("중지")  # 중지 가능
            self.startStopAction.setEnabled(True)
            self.pauseResumeAction.setText("재개")
            self.pauseResumeAction.setEnabled(True)
        elif state in [
            TimerState.IDLE,
            TimerState.FINISHED,
            TimerState.BREAK,
        ]:  # BREAK 상태 처리 추가 필요 시
            self.startStopAction.setText("시작")
            self.startStopAction.setEnabled(True)
            self.pauseResumeAction.setText("일시정지")
            self.pauseResumeAction.setEnabled(False)

        # 3. 트레이 액션 업데이트
        if state == TimerState.RUNNING:
            self.trayStartStopAction.setText("중지")
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("일시정지")
            self.trayPauseResumeAction.setEnabled(True)
        elif state == TimerState.PAUSED:
            self.trayStartStopAction.setText("중지")  # 중지 가능
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("재개")
            self.trayPauseResumeAction.setEnabled(True)
        elif state in [TimerState.IDLE, TimerState.FINISHED, TimerState.BREAK]:
            self.trayStartStopAction.setText("시작")
            self.trayStartStopAction.setEnabled(True)
            self.trayPauseResumeAction.setText("일시정지")
            self.trayPauseResumeAction.setEnabled(False)
