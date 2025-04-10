"""
PaceKeeper Qt - 메인 윈도우 액션
사용자 액션 및 명령 처리 메서드 모음
"""

from PyQt6.QtWidgets import QApplication, QMessageBox

from app.utils.constants import SessionType
from app.views.dialogs.break_dialog import BreakDialog
from app.views.dialogs.category_dialog import CategoryDialog
from app.views.dialogs.log_dialog import LogDialog
from app.views.dialogs.settings_dialog import SettingsDialog
from app.views.dialogs.tag_dialog import TagDialog
from app.views.styles.advanced_theme_manager import AdvancedThemeManager


def open_settings(self):
    """설정 대화상자 열기"""
    # 테마 관리자의 단일 인스턴스 사용
    theme_manager = AdvancedThemeManager.get_instance(app=self.app_instance)
    
    settings_dialog = SettingsDialog(self, app_config=self.config, theme_manager=theme_manager)
    settings_dialog.settingsChanged.connect(self.on_settings_changed)
    result = settings_dialog.exec()
    
    if result:
        # 설정이 변경되면 UI 업데이트
        self.updateUI()


def open_log_dialog(self):
    """로그 대화상자 열기"""
    theme_manager = AdvancedThemeManager.get_instance(app=self.app_instance)
        
    log_dialog = LogDialog(
        self,
        theme_manager=theme_manager,
    )
    log_dialog.exec()

    # 대화상자가 닫힌 후 최근 로그 업데이트
    self.updateRecentLogs()


def open_category_dialog(self):
    """카테고리 대화상자 열기"""
    theme_manager = AdvancedThemeManager.get_instance(app=self.app_instance)
        
    category_dialog = CategoryDialog(
        self,
        theme_manager=theme_manager
    )
    category_dialog.exec()


def open_tag_dialog(self):
    """태그 대화상자 열기"""
    theme_manager = AdvancedThemeManager.get_instance(app=self.app_instance)
    
    tag_dialog = TagDialog(
        self, 
        theme_manager=theme_manager
    )
    tag_dialog.exec()

    # 대화상자가 닫힌 후 태그 목록 업데이트
    self.updateTags()


def show_break_dialog(self, session_type):
    """
    휴식 대화상자 표시

    Args:
        session_type: 세션 타입 (SHORT_BREAK 또는 LONG_BREAK)
    """
    theme_manager = AdvancedThemeManager.get_instance(app=self.app_instance)
    
    break_dialog = BreakDialog(self, session_type, theme_manager, self.config)

    # 휴식 시작 시그널 연결
    break_dialog.startBreakRequested.connect(
        lambda: self.main_controller.start_session(session_type)
    )

    # 휴식 건너뛰기 시그널 연결
    break_dialog.skipBreakRequested.connect(
        lambda: self.main_controller.start_session(SessionType.POMODORO)
    )

    # 대화상자 표시 - exec() 사용하여 모달 방식으로 표시
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


# 이벤트 핸들러는 원래 파일에서 이동
def on_settings_changed(self, settings):
    """
    설정 변경 이벤트 핸들러

    Args:
        settings: 변경된 설정 값
    """
    # UI 관련 설정 적용
    if "show_seconds" in settings:
        # showSeconds 메서드 호출 전 유효성 검사
        if hasattr(self.timerWidget, "showSeconds"):
            self.timerWidget.showSeconds(settings["show_seconds"])

    # 테마 관련 설정 변경 시 테마 적용
    if "theme" in settings and hasattr(self, "theme_manager"):
        # 테마 관리자 및 인스턴스 유효성 확인
        app = None
        if hasattr(self, "app_instance") and self.app_instance:
            app = self.app_instance
        else:
            app = QApplication.instance()
        
        if app:
            self.theme_manager.apply_theme(app, settings["theme"])
        else:
            # QApplication 인스턴스 없을 때는 테마 그만 적용
            style_content = self.theme_manager.get_theme_style(settings["theme"])
            if style_content:
                self.setStyleSheet(style_content)

    # 창 크기 관련 설정 적용
    if "main_dlg_width" in settings and "main_dlg_height" in settings:
        self.resize(settings["main_dlg_width"], settings["main_dlg_height"])

        # 반응형 스타일 다시 적용
        if hasattr(self, "responsive_style_manager"):
            self.responsive_style_manager.apply_responsive_style(
                self, settings["main_dlg_width"]
            )
