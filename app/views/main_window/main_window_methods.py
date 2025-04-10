"""
PaceKeeper Qt - 메인 윈도우 메서드 (개선된 버전)
UI 개선된 다이얼로그를 사용하는 개선된 메서드
"""

from PyQt6.QtWidgets import QApplication

from app.views.dialogs.category_dialog import CategoryDialog
from app.views.dialogs.log_dialog import LogDialog
from app.views.dialogs.settings_dialog import SettingsDialog
from app.views.dialogs.tag_dialog import TagDialog


def show_settings_dialog(self):
    """설정 대화상자 표시"""
    dialog = SettingsDialog(
        parent=self, controller_or_app_config=self.config, theme_manager=self.theme_manager
    )
    dialog.settingsChanged.connect(self.on_settings_changed)
    dialog.exec()


def show_log_dialog(self):
    """로그 대화상자 표시"""
    dialog = LogDialog(
        self, controller_or_service=self.controller, theme_manager=self.theme_manager
    )
    dialog.exec()


def show_category_dialog(self):
    """카테고리 대화상자 표시"""
    dialog = CategoryDialog(
        self,
        controller_or_service=self.controller.category_service,
        theme_manager=self.theme_manager,
    )
    dialog.exec()


def show_tag_dialog(self):
    """태그 대화상자 표시"""
    dialog = TagDialog(
        self,
        controller_or_service=self.controller.tag_service,
        category_service=self.controller.category_service,
        theme_manager=self.theme_manager,
    )
    dialog.exec()


def on_settings_changed(self, settings):
    """
    설정 변경 이벤트 핸들러

    Args:
        settings: 변경된 설정 값
    """
    # UI 관련 설정 적용
    if "show_seconds" in settings:
        self.timer_widget.set_show_seconds(settings["show_seconds"])

    # 테마 관련 설정 변경 시 테마 적용
    if "theme" in settings and hasattr(self, "theme_manager"):
        self.theme_manager.apply_theme(QApplication.instance(), settings["theme"])

    # 창 크기 관련 설정 적용
    if "main_dlg_width" in settings and "main_dlg_height" in settings:
        self.resize(settings["main_dlg_width"], settings["main_dlg_height"])

        # 반응형 스타일 다시 적용
        if hasattr(self, "responsive_style_manager"):
            self.responsive_style_manager.apply_responsive_style(
                self, settings["main_dlg_width"]
            )
