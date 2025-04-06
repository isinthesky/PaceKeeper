"""
PaceKeeper Qt - 반응형 스타일 관리자
창 크기에 따른 스타일 적용을 관리하는 클래스
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject


class ResponsiveStyleManager(QObject):
    """반응형 스타일 관리 클래스"""
    
    def __init__(self):
        super().__init__()
        self.base_styles = {}  # 기본 스타일 저장용 (위젯 ID별)
    
    def set_base_style(self, widget_id, style):
        """
        특정 위젯의 기본 스타일 설정
        
        Args:
            widget_id: 위젯 식별자
            style: 기본 스타일
        """
        self.base_styles[widget_id] = style
    
    def get_responsive_style(self, width, height=None):
        """
        창 크기에 따른 반응형 스타일 생성
        
        Args:
            width: 창 너비
            height: 창 높이 (선택 사항)
            
        Returns:
            str: 반응형 스타일 문자열
        """
        # 창 크기에 따른 툴바 및 상태바 스타일
        if width < 500:
            style = """
                QToolBar { 
                    font-size: 9pt; 
                }
                QToolBar QToolButton { 
                    padding: 3px; 
                }
                QStatusBar { 
                    font-size: 9pt; 
                }
                QPushButton {
                    min-width: 70px;
                    min-height: 25px;
                    padding: 3px 6px;
                }
                QLabel#timerLabel {
                    font-size: 28pt;
                }
            """
        elif width < 800:
            style = """
                QToolBar { 
                    font-size: 10pt; 
                }
                QToolBar QToolButton { 
                    padding: 4px; 
                }
                QStatusBar { 
                    font-size: 10pt; 
                }
                QPushButton {
                    min-width: 80px;
                    min-height: 28px;
                    padding: 4px 8px;
                }
                QLabel#timerLabel {
                    font-size: 36pt;
                }
            """
        else:
            style = """
                QToolBar { 
                    font-size: 11pt; 
                }
                QToolBar QToolButton { 
                    padding: 5px; 
                }
                QStatusBar { 
                    font-size: 10pt; 
                }
                QPushButton {
                    min-width: 90px;
                    min-height: 30px;
                    padding: 5px 10px;
                }
                QLabel#timerLabel {
                    font-size: 48pt;
                }
            """
        
        return style
    
    def apply_responsive_style(self, widget, width, height=None, preserve_theme=True):
        """
        위젯에 반응형 스타일 적용
        
        Args:
            widget: 스타일을 적용할 위젯
            width: 창 너비
            height: 창 높이 (선택 사항)
            preserve_theme: 기존 테마 스타일 유지 여부
        """
        # 반응형 스타일 생성
        responsive_style = self.get_responsive_style(width, height)
        
        # 현재 위젯 스타일
        current_style = widget.styleSheet()
        
        if preserve_theme and current_style:
            # 기존 테마 스타일과 반응형 스타일 결합
            # 간단한 구현을 위해 그냥 덧붙이는 방식 사용
            widget.setStyleSheet(current_style + "\n" + responsive_style)
        else:
            # 기존 스타일 무시하고 반응형 스타일만 적용
            widget.setStyleSheet(responsive_style)
