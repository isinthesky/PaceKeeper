# utils/theme_manager.py

import os
from typing import Optional

from PyQt5.QtWidgets import QApplication, QWidget

from pacekeeper.utils.resource_path import resource_path


class ThemeManager:
    """
    현대적인 테마 시스템 관리자
    
    QSS 스타일시트를 로드하고 적용하는 중앙화된 테마 관리 시스템
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
    
    def get_available_themes(self) -> dict[str, str]:
        """
        사용 가능한 테마 목록 반환
        
        Returns:
            dict[str, str]: 테마 ID와 이름의 매핑
        """
        return self._available_themes.copy()
    
    def load_theme(self, theme_name: str) -> Optional[str]:
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
            with open(theme_path, 'r', encoding='utf-8') as f:
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
    
    def apply_theme(self, widget: Optional[QWidget] = None, theme_name: Optional[str] = None) -> bool:
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
    
    def get_current_theme(self) -> str:
        """
        현재 활성 테마 이름 반환
        
        Returns:
            str: 현재 테마 이름
        """
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """
        테마 변경
        
        Args:
            theme_name: 새로운 테마 이름
            
        Returns:
            bool: 변경 성공 여부
        """
        if theme_name not in self._available_themes:
            print(f"알 수 없는 테마: {theme_name}")
            return False
        
        return self.apply_theme(theme_name=theme_name)
    
    def clear_cache(self) -> None:
        """테마 캐시 초기화"""
        self._themes_cache.clear()
    
    def reload_current_theme(self) -> bool:
        """
        현재 테마 다시 로드 (개발 시 유용)
        
        Returns:
            bool: 다시 로드 성공 여부
        """
        # 캐시에서 현재 테마 제거
        if self._current_theme in self._themes_cache:
            del self._themes_cache[self._current_theme]
        
        return self.apply_theme()
    
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
    
    @staticmethod
    def apply_card_style(widget: QWidget, card_type: str = "card") -> None:
        """
        위젯에 카드 스타일 적용
        
        Args:
            widget: 카드 스타일을 적용할 위젯
            card_type: 카드 타입 ("card", "maincard" 등)
        """
        ThemeManager.set_widget_property(widget, card_type, True)
    
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


# 전역 테마 매니저 인스턴스
theme_manager = ThemeManager()