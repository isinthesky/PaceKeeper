"""
PaceKeeper Qt - 반응형 스타일 관리자 (개선된 버전)
화면 크기에 따른 UI 요소 자동 조정
"""

from PyQt6.QtWidgets import QApplication


class ResponsiveStyleManager:
    """반응형 스타일 관리 클래스 - 개선된 버전"""

    def __init__(self):
        """반응형 스타일 관리자 초기화"""
        self.breakpoints = {"small": 500, "medium": 800, "large": 1200}

    def apply_responsive_style(self, window, width):
        """
        창 너비에 따른 반응형 스타일 적용

        Args:
            window: 대상 윈도우 인스턴스
            width: 창 너비
        """
        # 창 너비에 따른 스타일 선택
        if width < self.breakpoints["small"]:
            self._apply_small_screen_style(window)
        elif width < self.breakpoints["medium"]:
            self._apply_medium_screen_style(window)
        else:
            self._apply_large_screen_style(window)

    def _apply_small_screen_style(self, window):
        """
        작은 화면 스타일 적용

        Args:
            window: 대상 윈도우 인스턴스
        """
        # 컨트롤 크기 및 여백 축소
        style = """
            QLabel { font-size: 9pt; }
            QToolBar { font-size: 9pt; }
            QToolBar QToolButton { padding: 3px; margin: 1px; }
            QStatusBar { font-size: 9pt; }
            QDialog { min-width: 400px; }
            
            QLabel#timerLabel { 
                font-size: 32pt; 
                padding: 5px;
            }
            
            QPushButton { 
                min-width: 70px; 
                min-height: 28px; 
                padding: 4px 8px;
                font-size: 9pt;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                padding: 4px 6px;
                min-height: 24px;
                font-size: 9pt;
            }
            
            QGroupBox {
                margin-top: 12px;
                padding-top: 12px;
                font-size: 9pt;
            }
            
            QTabBar::tab {
                padding: 6px 10px;
                min-width: 60px;
                font-size: 9pt;
            }
            
            QListWidget::item, QTreeWidget::item, QTableWidget::item {
                padding: 6px;
                font-size: 9pt;
            }
            
            QHeaderView::section {
                padding: 4px;
                font-size: 9pt;
            }
        """

        # 현재 스타일시트에 추가
        current_style = window.styleSheet()
        window.setStyleSheet(current_style + style)

    def _apply_medium_screen_style(self, window):
        """
        중간 화면 스타일 적용

        Args:
            window: 대상 윈도우 인스턴스
        """
        # 표준 크기의 컨트롤
        style = """
            QLabel { font-size: 10pt; }
            QToolBar { font-size: 10pt; }
            QToolBar QToolButton { padding: 4px; margin: 2px; }
            QStatusBar { font-size: 10pt; }
            QDialog { min-width: 500px; }
            
            QLabel#timerLabel { 
                font-size: 42pt; 
                padding: 8px;
            }
            
            QPushButton { 
                min-width: 80px; 
                min-height: 32px; 
                padding: 6px 12px;
                font-size: 10pt;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                padding: 6px 8px;
                min-height: 28px;
                font-size: 10pt;
            }
            
            QGroupBox {
                margin-top: 16px;
                padding-top: 16px;
                font-size: 10pt;
            }
            
            QTabBar::tab {
                padding: 8px 14px;
                min-width: 80px;
                font-size: 10pt;
            }
            
            QListWidget::item, QTreeWidget::item, QTableWidget::item {
                padding: 8px;
                font-size: 10pt;
            }
            
            QHeaderView::section {
                padding: 6px;
                font-size: 10pt;
            }
        """

        # 현재 스타일시트에 추가
        current_style = window.styleSheet()
        window.setStyleSheet(current_style + style)

    def _apply_large_screen_style(self, window):
        """
        큰 화면 스타일 적용

        Args:
            window: 대상 윈도우 인스턴스
        """
        # 더 큰 컨트롤 및 여유로운 레이아웃
        style = """
            QLabel { font-size: 11pt; }
            QToolBar { font-size: 11pt; }
            QToolBar QToolButton { padding: 5px; margin: 3px; }
            QStatusBar { font-size: 11pt; }
            QDialog { min-width: 600px; }
            
            QLabel#timerLabel { 
                font-size: 52pt; 
                padding: 10px;
            }
            
            QPushButton { 
                min-width: 100px; 
                min-height: 36px; 
                padding: 8px 16px;
                font-size: 11pt;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                padding: 8px 12px;
                min-height: 32px;
                font-size: 11pt;
            }
            
            QGroupBox {
                margin-top: 20px;
                padding-top: 20px;
                font-size: 11pt;
            }
            
            QTabBar::tab {
                padding: 10px 18px;
                min-width: 100px;
                font-size: 11pt;
            }
            
            QListWidget::item, QTreeWidget::item, QTableWidget::item {
                padding: 10px;
                font-size: 11pt;
            }
            
            QHeaderView::section {
                padding: 8px;
                font-size: 11pt;
            }
        """

        # 현재 스타일시트에 추가
        current_style = window.styleSheet()
        window.setStyleSheet(current_style + style)
