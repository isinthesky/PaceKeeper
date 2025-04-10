"""
PaceKeeper Qt - Tag Widget
태그 버튼을 표시하는 위젯 구현
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QSizePolicy, QVBoxLayout, QWidget)


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
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)

        # 헤더 레이블
        self.headerLabel = QLabel("Tags")
        self.headerLabel.setObjectName("sectionHeader")
        self.mainLayout.addWidget(self.headerLabel)

        # 스크롤 영역
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setMaximumHeight(60)

        # 스크롤 영역 내부 위젯
        self.scrollContent = QWidget()
        self.scrollLayout = QHBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(5)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.scrollArea.setWidget(self.scrollContent)
        self.mainLayout.addWidget(self.scrollArea)

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

            try:
                if item:    
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            except Exception as e:
                print(f"[DEBUG] 태그 버튼 삭제 중 오류 발생: {e}")

    def update_tags(self, tags):
        """태그 버튼 일괄 업데이트

        Args:
            tags: TagEntity 목록
        """
        # 기존 버튼 삭제
        self.clear()

        # 새 태그 추가
        for tag in tags:
            # TagEntity에서 필요한 정보 추출
            tag_name = tag.name if hasattr(tag, "name") else str(tag)
            # 색상이 있으면 적용
            color = tag.color if hasattr(tag, "color") else None
            self.addTag(tag_name, color)
