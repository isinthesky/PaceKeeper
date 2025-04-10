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

        # 태그 버튼 스타일 지정
        style = ""
        
        if color:
            # 색상이 지정되었다면 배경색으로 설정
            text_color = "#FFFFFF" if self._is_dark_color(color) else "#000000"
            style = f"background-color: {color}; color: {text_color}; border: none; border-radius: 5px; padding: 3px 8px;"
        
        button.setStyleSheet(style)
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
            
            # 카테고리 색상 사용
            color = tag.category_color if hasattr(tag, "category_color") else None
            self.addTag(tag_name, color)
            
    def _is_dark_color(self, hex_color):
        """
        색상이 어두운지 확인
        
        Args:
            hex_color: HEX 색상 문자열 (#RRGGBB)
            
        Returns:
            어두운 색상이면 True, 밝은 색상이면 False
        """
        # # 제거
        hex_color = hex_color.lstrip('#')
        
        # 기본값
        if len(hex_color) != 6:
            return False
            
        # RGB 값 추출
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # 색상의 밝기 계산 (YIQ 공식)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            
            # 128보다 작으면 어두운 색상
            return brightness < 128
        except ValueError:
            return False
