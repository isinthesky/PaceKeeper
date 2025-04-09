"""
PaceKeeper Qt - 태그 대화상자
태그 관리 UI
"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QHBoxLayout,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from app.domain.category.category_service import CategoryService
from app.domain.tag.tag_entity import TagEntity
from app.domain.tag.tag_service import TagService
from app.views.styles.advanced_theme_manager import AdvancedThemeManager


class TagDialog(QDialog):
    """태그 관리 대화상자 클래스"""

    def __init__(
        self, parent=None, tag_service=None, category_service=None, theme_manager=None
    ):
        """
        태그 대화상자 초기화

        Args:
            parent: 부모 위젯
            tag_service: 태그 서비스 인스턴스
            category_service: 카테고리 서비스 인스턴스
            theme_manager: 테마 관리자 인스턴스
        """
        super().__init__(parent)

        self.tag_service = tag_service or TagService()
        self.category_service = category_service or CategoryService()
        self.theme_manager = theme_manager or AdvancedThemeManager()
        self.current_tag = None
        self.categories = {}

        if self.theme_manager:
            self.theme_manager.register_widget(self)

        self.setupUI()

        self.loadCategories()

        self.loadTags()

        self.connectSignals()

    def setupUI(self):
        """UI 초기화"""
        self.setWindowTitle("태그 관리")
        self.resize(450, 350)

        self.main_layout = QHBoxLayout(self)

        self.leftPanel = QWidget()
        self.leftLayout = QVBoxLayout(self.leftPanel)

        self.listLabel = QLabel("태그 목록")
        self.leftLayout.addWidget(self.listLabel)

        self.tagList = QListWidget()
        self.tagList.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.leftLayout.addWidget(self.tagList)

        self.buttonLayout = QHBoxLayout()

        self.addButton = QPushButton("추가")
        self.removeButton = QPushButton("삭제")

        self.buttonLayout.addWidget(self.addButton)
        self.buttonLayout.addWidget(self.removeButton)
        self.leftLayout.addLayout(self.buttonLayout)

        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout(self.rightPanel)

        self.editLabel = QLabel("태그 편집")
        self.rightLayout.addWidget(self.editLabel)

        self.editForm = QFormLayout()

        self.nameInput = QLineEdit()
        self.editForm.addRow("이름:", self.nameInput)

        self.categoryComboBox = QComboBox()
        self.editForm.addRow("카테고리:", self.categoryComboBox)

        self.rightLayout.addLayout(self.editForm)

        self.actionLayout = QHBoxLayout()
        self.saveButton = QPushButton("저장")
        self.cancelButton = QPushButton("취소")
        self.actionLayout.addWidget(self.saveButton)
        self.actionLayout.addWidget(self.cancelButton)
        self.rightLayout.addLayout(self.actionLayout)

        self.rightLayout.addStretch(1)

        self.main_layout.addWidget(self.leftPanel, 1)
        self.main_layout.addWidget(self.rightPanel, 1)

        self.enableEditForm(False)

    def connectSignals(self):
        """시그널 연결"""
        self.tagList.currentItemChanged.connect(self.onTagSelected)

        self.addButton.clicked.connect(self.onAddTag)
        self.removeButton.clicked.connect(self.onRemoveTag)
        self.saveButton.clicked.connect(self.onSaveTag)
        self.cancelButton.clicked.connect(self.onCancelEdit)

    def loadCategories(self):
        """카테고리 목록 로드 및 콤보박스 채우기"""
        self.categoryComboBox.clear()
        self.categories.clear()

        self.categoryComboBox.addItem("없음", None)
        self.categories[None] = {"name": "없음", "color": "#808080"}

        try:
            categories_list = self.category_service.get_all_categories()
            for category in categories_list:
                self.categoryComboBox.addItem(category.name, category.id)
                self.categories[category.id] = {
                    "name": category.name,
                    "color": category.color,
                }
        except Exception as e:
            print(f"카테고리 로드 실패: {e}")
            QMessageBox.warning(
                self, "오류", "카테고리 목록을 불러오는 중 오류가 발생했습니다."
            )

    def loadTags(self):
        """태그 목록 로드 및 카테고리 색상 적용"""
        self.tagList.clear()

        tags = self.tag_service.get_all_tags()

        for tag in tags:
            item = QListWidgetItem(f"#{tag.name}")
            item.setData(Qt.ItemDataRole.UserRole, tag)

            category_info = self.categories.get(tag.category_id)
            color_hex = (
                category_info["color"]
                if category_info
                else self.categories[None]["color"]
            )
            color = QColor(color_hex)
            item.setForeground(QBrush(color))

            self.tagList.addItem(item)

    def enableEditForm(self, enabled):
        """
        편집 폼 활성화 상태 변경

        Args:
            enabled: 활성화 여부
        """
        self.nameInput.setEnabled(enabled)
        self.categoryComboBox.setEnabled(enabled)
        self.saveButton.setEnabled(enabled)
        self.cancelButton.setEnabled(enabled)

        if not enabled:
            self.nameInput.clear()
            self.categoryComboBox.setCurrentIndex(0)
            self.current_tag = None

    def isNewTag(self):
        """
        현재 편집 중인 태그가 새 태그인지 확인

        Returns:
            새 태그 여부
        """
        return self.current_tag is not None and self.current_tag.id is None

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def onTagSelected(self, current, previous):
        """
        태그 선택 이벤트 핸들러

        Args:
            current: 현재 선택된 항목
            previous: 이전 선택된 항목
        """
        if current:
            tag = current.data(Qt.ItemDataRole.UserRole)

            self.current_tag = tag

            self.nameInput.setText(tag.name)

            if tag.category_id is not None and tag.category_id in self.categories:
                index = self.categoryComboBox.findData(tag.category_id)
                self.categoryComboBox.setCurrentIndex(index if index >= 0 else 0)
            else:
                self.categoryComboBox.setCurrentIndex(0)

            self.enableEditForm(True)
        else:
            self.enableEditForm(False)

    @pyqtSlot()
    def onAddTag(self):
        """태그 추가 버튼 이벤트 핸들러"""
        new_tag = TagEntity(id=None, name="new_tag")

        self.current_tag = new_tag

        self.nameInput.setText(new_tag.name)
        self.categoryComboBox.setCurrentIndex(0)

        self.enableEditForm(True)

        self.nameInput.setFocus()
        self.nameInput.selectAll()

    @pyqtSlot()
    def onRemoveTag(self):
        """태그 삭제 버튼 이벤트 핸들러"""
        current_item = self.tagList.currentItem()
        if not current_item:
            return

        tag = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "태그 삭제",
            f"'#{tag.name}' 태그를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tag_service.delete_tag(tag.id)

            self.loadTags()

            self.enableEditForm(False)

    @pyqtSlot()
    def onSaveTag(self):
        """태그 저장 버튼 이벤트 핸들러"""
        name = self.nameInput.text().strip()
        if name.startswith("#"):
            name = name[1:]

        if not name:
            QMessageBox.warning(self, "입력 오류", "태그 이름을 입력하세요.")
            self.nameInput.setFocus()
            return

        selected_category_id = self.categoryComboBox.currentData()

        if self.current_tag:
            self.current_tag.name = name
            self.current_tag.category_id = selected_category_id

            if self.isNewTag():
                self.tag_service.create_tag(
                    name=self.current_tag.name, category_id=self.current_tag.category_id
                )
            else:
                self.tag_service.update_tag(self.current_tag)

            self.loadTags()

            self.enableEditForm(False)

    @pyqtSlot()
    def onCancelEdit(self):
        """편집 취소 버튼 이벤트 핸들러"""
        self.enableEditForm(False)

        self.tagList.clearSelection()

    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        if self.theme_manager:
            self.theme_manager.unregister_widget(self)
        super().closeEvent(event)
