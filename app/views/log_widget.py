"""
PaceKeeper Qt - Log Widget
로그 항목을 표시하는 위젯 구현
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QLabel, QListWidget, QListWidgetItem, QVBoxLayout,
                             QWidget)


class LogListWidget(QWidget):
    """로그 목록 위젯 클래스"""

    # 사용자 정의 시그널
    logSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """UI 초기화"""
        # 메인 레이아웃
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 헤더 레이블
        self.headerLabel = QLabel("Recent Logs")
        self.headerLabel.setObjectName("sectionHeader")
        self.layout.addWidget(self.headerLabel)

        # 리스트 위젯
        self.listWidget = QListWidget()
        self.listWidget.itemDoubleClicked.connect(self.onItemDoubleClicked)

        # 레이아웃에 위젯 추가
        self.layout.addWidget(self.listWidget)

    def addLogItem(self, logText, tags=None):
        """로그 항목 추가"""
        item = QListWidgetItem(logText)
        if tags:
            item.setData(Qt.ItemDataRole.UserRole, tags)
        self.listWidget.addItem(item)

    def onItemDoubleClicked(self, item):
        """항목 더블 클릭 이벤트 핸들러"""
        self.logSelected.emit(item.text())

    def clear(self):
        """모든 로그 항목 삭제"""
        self.listWidget.clear()
