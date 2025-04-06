"""
PaceKeeper Qt - Tag Widget
태그 버튼을 표시하는 위젯 구현
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QScrollArea, QFrame, 
                            QPushButton, QSizePolicy, QLabel, QVBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt


class TagButtonsWidget(QWidget):
    """태그 버튼 위젯 클래스"""
    
    # 사용자 정의 시그널
    tagSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
    
    def setupUI(self):
        """UI 초기화"""
        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # 헤더 레이블
        self.headerLabel = QLabel("Tags")
        self.headerLabel.setObjectName("sectionHeader")
        self.layout.addWidget(self.headerLabel)
        
        # 스크롤 영역
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setMaximumHeight(60)
        
        # 스크롤 영역 내부 위젯
        self.scrollContent = QWidget()
        self.scrollLayout = QHBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(5)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scrollArea.setWidget(self.scrollContent)
        self.layout.addWidget(self.scrollArea)
    
    def addTag(self, tagName, color=None):
        """태그 버튼 추가"""
        button = QPushButton(f"#{tagName}")
        button.setObjectName("tagButton")
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        button.clicked.connect(lambda: self.onTagClicked(tagName))
        
        if color:
            button.setStyleSheet(f"background-color: {color};")
        
        self.scrollLayout.addWidget(button)
        return button
    
    def onTagClicked(self, tagName):
        """태그 버튼 클릭 이벤트 핸들러"""
        self.tagSelected.emit(tagName)
    
    def clear(self):
        """모든 태그 버튼 삭제"""
        while self.scrollLayout.count():
            item = self.scrollLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
