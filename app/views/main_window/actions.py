"""
PaceKeeper Qt - 메인 윈도우 액션
사용자 액션 및 명령 처리 메서드 모음
"""

from PyQt6.QtWidgets import QMessageBox

from app.utils.constants import TimerState, SessionType
from app.views.dialogs.settings_dialog import SettingsDialog
from app.views.dialogs.log_dialog import LogDialog
from app.views.dialogs.category_dialog import CategoryDialog
from app.views.dialogs.tag_dialog import TagDialog
from app.views.dialogs.break_dialog import BreakDialog


def toggle_timer(self):
    """타이머 시작/중지 토글"""
    timer_state = self.timer_controller.get_state()
    
    if timer_state in [TimerState.IDLE, TimerState.FINISHED]:
        # 타이머 시작
        self.main_controller.start_session()
    else:
        # 타이머 중지
        self.main_controller.stop_session()


def toggle_pause(self):
    """타이머 일시정지/재개 토글"""
    self.main_controller.toggle_pause()


def open_settings(self):
    """설정 대화상자 열기"""
    settings_dialog = SettingsDialog(self, self.config, self.theme_manager)
    result = settings_dialog.exec()
    if result:
        # 설정이 변경되면 UI 업데이트
        self.updateUI()


def open_log_dialog(self):
    """로그 대화상자 열기"""
    log_dialog = LogDialog(self, self.log_service, self.category_service)
    log_dialog.exec()
    
    # 대화상자가 닫힌 후 최근 로그 업데이트
    self.updateRecentLogs()


def open_category_dialog(self):
    """카테고리 대화상자 열기"""
    category_dialog = CategoryDialog(self, self.category_service)
    category_dialog.exec()


def open_tag_dialog(self):
    """태그 대화상자 열기"""
    tag_dialog = TagDialog(self, self.tag_service)
    tag_dialog.exec()
    
    # 대화상자가 닫힌 후 태그 목록 업데이트
    self.updateTags()


def show_break_dialog(self, session_type):
    """
    휴식 대화상자 표시
    
    Args:
        session_type: 세션 타입 (SHORT_BREAK 또는 LONG_BREAK)
    """
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


def show_stats(self):
    """통계 보기"""
    # 실제 구현에서는 통계 대화상자 생성 및 표시
    QMessageBox.information(self, "통계", "통계 기능은 개발 중입니다.")


def show_help(self):
    """도움말 표시"""
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


def show_about(self):
    """정보 대화상자 표시"""
    about_text = """
    <h3>PaceKeeper</h3>
    <p>버전: 2.0.0</p>
    <p>간단하고 효과적인 시간 관리 도구</p>
    <p>© 2023 PaceKeeper Team</p>
    <p>Qt 프레임워크 기반 마이그레이션 완료 버전</p>
    """
    QMessageBox.about(self, "PaceKeeper 정보", about_text)
