"""
PaceKeeper Qt - 메인 윈도우
애플리케이션 메인 윈도우 리팩토링된 구현
"""

from PyQt6.QtWidgets import QMainWindow

from app.config.app_config import AppConfig
from app.controllers.main_controller import MainController
from app.controllers.timer_controller import TimerController
from app.domain.log.log_service import LogService
from app.domain.tag.tag_service import TagService
from app.domain.category.category_service import CategoryService
from app.views.styles.advanced_theme_manager import AdvancedThemeManager

# 리팩토링된 모듈 임포트
from app.views.main_window.ui_setup import setup_ui, setup_tray_icon
from app.views.main_window.event_handlers import (
    connect_signals, on_timer_start, on_timer_pause, on_timer_state_changed,
    on_session_started, on_session_paused, on_session_resumed,
    on_session_stopped, on_session_finished, on_text_submitted,
    on_tag_selected, on_log_selected, on_tray_icon_activated,
    on_exit_from_tray, close_event
)
from app.views.main_window.actions import (
    toggle_timer, toggle_pause, open_settings, open_log_dialog,
    open_category_dialog, open_tag_dialog, show_break_dialog,
    show_stats, show_help, show_about
)
from app.views.main_window.ui_updates import (
    update_ui, update_recent_logs, update_tags
)


class MainWindow(QMainWindow):
    """애플리케이션 메인 윈도우 클래스"""
    
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
        
        # 서비스 초기화
        self.log_service = LogService()
        self.tag_service = TagService()
        self.category_service = CategoryService()
        
        # 컨트롤러 초기화
        self.timer_controller = TimerController()
        self.main_controller = MainController(
            app_config=self.config,
            timer_controller=self.timer_controller,
            log_service=self.log_service,
            tag_service=self.tag_service,
            category_service=self.category_service
        )
        
        # UI 초기화 메서드 바인딩
        setup_ui(self)
        setup_tray_icon(self)
        
        # 이벤트 핸들러 메서드 바인딩
        self.onTimerStart = lambda: on_timer_start(self)
        self.onTimerPause = lambda: on_timer_pause(self)
        self.onTimerStateChanged = lambda state: on_timer_state_changed(self, state)
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
        
        # 액션 메서드 바인딩
        self.toggleTimer = lambda: toggle_timer(self)
        self.togglePause = lambda: toggle_pause(self)
        self.openSettings = lambda: open_settings(self)
        self.openLogDialog = lambda: open_log_dialog(self)
        self.openCategoryDialog = lambda: open_category_dialog(self)
        self.openTagDialog = lambda: open_tag_dialog(self)
        self.showBreakDialog = lambda session_type: show_break_dialog(self, session_type)
        self.showStats = lambda: show_stats(self)
        self.showHelp = lambda: show_help(self)
        self.showAbout = lambda: show_about(self)
        
        # UI 업데이트 메서드 바인딩
        self.updateUI = lambda: update_ui(self)
        self.updateRecentLogs = lambda: update_recent_logs(self)
        self.updateTags = lambda: update_tags(self)
        
        # 시그널 연결
        connect_signals(self)
        
        # 초기 상태 설정
        self.updateUI()
    
    def closeEvent(self, event):
        """
        창 닫기 이벤트 처리
        
        Args:
            event: 닫기 이벤트
        """
        close_event(self, event)
        
    def toggleTimer(self):
        """타이머 시작/중지 토글"""
        timer_state = self.timer_controller.get_state()
        
        from app.utils.constants import TimerState
        if timer_state in [TimerState.IDLE, TimerState.FINISHED]:
            # 현재 입력된 텍스트 가져오기
            current_text = self.textInputWidget.text()
            
            # 텍스트가 있으면 로그 등록
            if current_text and current_text.strip():
                # 현재 시간으로 로그 생성
                from datetime import datetime
                start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 로그 생성
                self.log_service.create_log(
                    message=current_text,
                    start_date=start_date
                )
                
                # 최근 로그 업데이트
                self.updateRecentLogs()
            
            # 타이머 시작
            self.main_controller.start_session()
        else:
            # 타이머 중지
            self.main_controller.stop_session()
            
    def togglePause(self):
        """타이머 일시정지/재개 토글"""
        self.main_controller.toggle_pause()
        
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
        log_dialog = LogDialog(self, self.log_service, self.category_service)
        log_dialog.exec()
        
        # 대화상자가 닫힌 후 최근 로그 업데이트
        self.updateRecentLogs()
        
    def openCategoryDialog(self):
        """카테고리 대화상자 열기"""
        from app.views.dialogs.category_dialog import CategoryDialog
        category_dialog = CategoryDialog(self, self.category_service)
        category_dialog.exec()
        
    def openTagDialog(self):
        """태그 대화상자 열기"""
        from app.views.dialogs.tag_dialog import TagDialog
        tag_dialog = TagDialog(self, self.tag_service)
        tag_dialog.exec()
        
        # 대화상자가 닫힌 후 태그 목록 업데이트
        self.updateTags()
        
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

    def updateTimerDisplay(self, timeStr):
        """
        타이머 표시 업데이트
        
        Args:
            timeStr: 표시할 시간 문자열
        """
        self.timerLabel.setText(timeStr)
            
    def _restore_normal_ui(self):
        """일반 모드 UI로 복원"""
        # 미니 버튼 컨테이너 숨기기
        self.miniButtonContainer.hide()
        
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
