"""
PaceKeeper Qt - Theme Manager
테마 관리 및 적용 클래스
"""

import os

from PyQt6.QtCore import QFile, QObject, QTextStream, pyqtSignal


class ThemeManager(QObject):
    """테마 관리 및 적용 클래스"""

    # 사용자 정의 시그널
    themeChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.currentTheme = "default"
        self.themesDir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "themes"
        )

        # 테마 목록
        self.themes = {
            "default": os.path.join(self.themesDir, "default.qss"),
            "dark": os.path.join(self.themesDir, "dark.qss"),
        }

    def availableThemes(self):
        """사용 가능한 테마 목록 반환"""
        return list(self.themes.keys())

    def currentThemeName(self):
        """현재 테마 이름 반환"""
        return self.currentTheme

    def applyTheme(self, app, themeName="default"):
        """애플리케이션에 테마 적용"""
        if themeName in self.themes:
            self.currentTheme = themeName
            qssPath = self.themes[themeName]

            try:
                with open(qssPath, "r") as f:
                    app.setStyleSheet(f.read())
                self.themeChanged.emit(themeName)
                return True
            except Exception as e:
                print(f"테마 적용 실패: {e}")

        return False
