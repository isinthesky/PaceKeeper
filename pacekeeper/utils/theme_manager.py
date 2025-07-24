# utils/theme_manager.py

import os
from typing import Optional

from PyQt5.QtWidgets import QApplication, QWidget

from pacekeeper.consts.colors import COLORS, is_valid_hex_color
from pacekeeper.utils.resource_path import resource_path


class ThemeManager:
    """
    현대적인 테마 시스템 관리자
    
    QSS 스타일시트를 로드하고 적용하는 중앙화된 테마 관리 시스템
    색상 관리, 동적 스타일 적용, 테마 전환 등의 기능을 제공합니다.
    """

    _instance: Optional['ThemeManager'] = None
    _current_theme: str = "modern_light"
    _themes_cache: dict[str, str] = {}

    def __new__(cls) -> 'ThemeManager':
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """테마 매니저 초기화"""
        if not hasattr(self, '_initialized'):
            self._available_themes = {
                "modern_light": "Modern Light Theme",
                "modern_dark": "Modern Dark Theme"
            }
            self._initialized = True

    # get_available_themes 메서드 제거됨 - 현재 단일 테마만 사용 중

    def load_theme(self, theme_name: str) -> str | None:
        """
        테마 스타일시트 로드
        
        Args:
            theme_name: 로드할 테마 이름
            
        Returns:
            Optional[str]: 스타일시트 내용 또는 None (로드 실패 시)
        """
        # 캐시에서 먼저 확인
        if theme_name in self._themes_cache:
            return self._themes_cache[theme_name]

        # 스타일시트 파일 경로 생성
        theme_file = f"{theme_name}.qss"
        theme_path = resource_path(f"assets/styles/{theme_file}")

        try:
            # 파일이 존재하지 않으면 절대 경로로 시도
            if not os.path.exists(theme_path):
                theme_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "assets", "styles", theme_file
                )

            # 스타일시트 파일 읽기
            with open(theme_path, encoding='utf-8') as f:
                stylesheet_content = f.read()

            # 캐시에 저장
            self._themes_cache[theme_name] = stylesheet_content

            return stylesheet_content

        except FileNotFoundError:
            print(f"테마 파일을 찾을 수 없습니다: {theme_path}")
            return None
        except Exception as e:
            print(f"테마 로드 중 오류 발생: {e}")
            return None

    def apply_theme(self, widget: QWidget | None = None, theme_name: str | None = None) -> bool:
        """
        위젯에 테마 적용
        
        Args:
            widget: 테마를 적용할 위젯 (None이면 QApplication 전체에 적용)
            theme_name: 적용할 테마 이름 (None이면 현재 테마 사용)
            
        Returns:
            bool: 적용 성공 여부
        """
        target_theme = theme_name or self._current_theme
        stylesheet = self.load_theme(target_theme)

        if stylesheet is None:
            return False

        try:
            if widget is None:
                # 전체 애플리케이션에 적용
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(stylesheet)
            else:
                # 특정 위젯에 적용
                widget.setStyleSheet(stylesheet)

            # 현재 테마 업데이트
            if theme_name:
                self._current_theme = target_theme

            return True

        except Exception as e:
            print(f"테마 적용 중 오류 발생: {e}")
            return False

    # get_current_theme 메서드 제거됨 - 현재 단일 테마만 사용 중

    # set_theme 메서드 제거됨 - 현재 단일 테마만 사용 중

    # clear_cache 메서드 제거됨 - 현재 사용되지 않음

    # reload_current_theme 메서드 제거됨 - 개발 중이지만 현재 사용되지 않음

    @staticmethod
    def set_widget_property(widget: QWidget, property_name: str, value: any) -> None:
        """
        위젯에 커스텀 속성 설정 (QSS 선택자용)
        
        Args:
            widget: 속성을 설정할 위젯
            property_name: 속성 이름
            value: 속성 값
        """
        widget.setProperty(property_name, value)
        # 스타일 새로고침을 위해 polish 호출
        widget.style().polish(widget)

    # apply_card_style 메서드 제거됨 - 카드 스타일이 QSS에서 제거되어 더 이상 사용되지 않음

    @staticmethod
    def apply_button_style(widget: QWidget, button_type: str = "primary") -> None:
        """
        버튼에 스타일 타입 적용
        
        Args:
            widget: 스타일을 적용할 버튼
            button_type: 버튼 타입 ("primary", "success", "warning", "secondary" 등)
        """
        ThemeManager.set_widget_property(widget, button_type, True)

    @staticmethod
    def apply_label_style(widget: QWidget, label_type: str = "title") -> None:
        """
        라벨에 스타일 타입 적용
        
        Args:
            widget: 스타일을 적용할 라벨
            label_type: 라벨 타입 ("title", "subtitle", "caption", "timer" 등)
        """
        ThemeManager.set_widget_property(widget, label_type, True)

    @staticmethod
    def apply_color(widget: QWidget, color: str, css_property: str = "background-color") -> None:
        """
        위젯에 동적 색상 적용
        
        Args:
            widget: 색상을 적용할 위젯
            color: 적용할 색상 (헥스 코드)
            css_property: CSS 속성명 (background-color, color, border-color 등)
        """
        if not is_valid_hex_color(color):
            color = COLORS.WHITE

        # 기존 스타일을 유지하면서 색상만 변경
        current_style = widget.styleSheet()
        new_style = f"{current_style}; {css_property}: {color};"
        widget.setStyleSheet(new_style)

    @staticmethod
    def apply_category_color(widget: QWidget, color: str, widget_type: str = "tag") -> None:
        """
        카테고리 색상을 위젯에 적용 (QSS 선택자 기반)
        
        Args:
            widget: 색상을 적용할 위젯
            color: 카테고리 색상
            widget_type: 위젯 타입 (tag, button 등)
        """
        if not is_valid_hex_color(color):
            color = COLORS.WHITE

        # QSS 선택자와 함께 색상 적용
        style = f"QPushButton[{widget_type}=true] {{ background-color: {color}; }}"
        widget.setStyleSheet(style)

    # apply_mini_mode 메서드 제거됨 - set_widget_property를 직접 사용하는 것으로 대체됨

    @staticmethod
    def apply_break_dialog_style(widget: QWidget, break_color: str = None) -> None:
        """
        휴식 다이얼로그 전용 스타일 적용
        
        Args:
            widget: 휴식 다이얼로그 위젯
            break_color: 휴식 배경 색상 (선택사항)
        """
        ThemeManager.set_widget_property(widget, "break", True)

        if break_color and is_valid_hex_color(break_color):
            # 배경 색상과 함께 추가 스타일 적용
            style = f"""
            QDialog[break=true] {{
                background-color: {break_color};
                border-radius: 20px;
                border: none;
            }}
            """
            widget.setStyleSheet(style)

    # get_color 메서드 제거됨 - COLORS 객체를 직접 사용하는 것으로 대체됨

    # get_colors 메서드 제거됨 - get_theme_colors() 함수를 직접 사용하는 것으로 대체됨


# 전역 테마 매니저 인스턴스
theme_manager = ThemeManager()
