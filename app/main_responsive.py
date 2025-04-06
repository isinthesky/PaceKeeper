"""
PaceKeeper Qt - 메인 애플리케이션 (반응형)
애플리케이션 진입점 - 고급 테마 및 반응형 UI 적용
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale

from app.config.app_config import AppConfig
from app.views.main_window import MainWindow
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.styles.responsive_style_manager import ResponsiveStyleManager


def main():
    """애플리케이션 진입점"""
    # QApplication 인스턴스 생성
    app = QApplication(sys.argv)
    app.setApplicationName("PaceKeeper")
    app.setOrganizationName("PaceKeeper Team")
    app.setOrganizationDomain("pacekeeper.com")
    
    # 언어 설정
    locale = QLocale.system()
    QLocale.setDefault(locale)
    
    # 설정 로드
    config = AppConfig()
    
    # 테마 관리자 생성 및 테마 적용
    theme_manager = AdvancedThemeManager()
    
    # 고급 또는 일반 테마 적용 (설정에 따라)
    if config.get("use_advanced_theme", False):
        theme = "advanced"
    else:
        theme = config.get("theme", "default")
        
    theme_manager.apply_theme(app, theme)
    
    # 반응형 스타일 관리자 생성
    responsive_style_manager = ResponsiveStyleManager()
    
    # 메인 윈도우 생성 (반응형)
    window = MainWindow(config, theme_manager)
    
    # 초기 반응형 스타일 적용
    initial_width = window.width()
    responsive_style_manager.apply_responsive_style(window, initial_width)
    
    # 윈도우 표시
    window.show()
    
    def cleanup():
        print("애플리케이션 종료 전 정리 작업을 수행합니다...")
        # 필요한 정리 작업 수행
    
    app.aboutToQuit.connect(cleanup)
    
    # 애플리케이션 실행
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
