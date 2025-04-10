"""
PaceKeeper Qt - Text Input Widget
로그 내용 입력을 위한 위젯 구현
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget)


class TextInputWidget(QWidget):
    """텍스트 입력 위젯 클래스"""

    # 사용자 정의 시그널
    textSubmitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """UI 초기화"""
        # 메인 레이아웃
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)

        # 헤더 레이블
        self.headerLabel = QLabel("Log Entry")
        self.headerLabel.setObjectName("sectionHeader")
        self.mainLayout.addWidget(self.headerLabel)

        # 입력 레이아웃
        self.inputLayout = QHBoxLayout()

        # 텍스트 입력 필드
        self.textInput = QLineEdit()
        self.textInput.setPlaceholderText("작업 내용을 입력하세요... (#태그 포함)")
        self.textInput.returnPressed.connect(self.onSubmitClicked)

        # 입력 레이아웃에 위젯 추가
        self.inputLayout.addWidget(self.textInput)

        # 메인 레이아웃에 입력 레이아웃 추가
        self.mainLayout.addLayout(self.inputLayout)

    def onSubmitClicked(self):
        """제출 버튼 클릭 이벤트 핸들러"""
        text = self.textInput.text().strip()
        if text:
            self.textSubmitted.emit(text)
            self.textInput.clear()

    def text(self):
        """입력 필드의 텍스트 반환"""
        return self.textInput.text()

    def clear(self):
        """입력 필드 내용 지우기"""
        self.textInput.clear()
        
    def setText(self, text):
        """입력 필드에 텍스트 설정
        
        Args:
            text: 설정할 텍스트
        """
        self.textInput.setText(text)
        
    # 호환성을 위한 메서드 (setPlainText -> setText 매핑)
    def setPlainText(self, text):
        """입력 필드에 텍스트 설정 (호환성 메서드)
        
        Args:
            text: 설정할 텍스트
        """
        self.setText(text)
