"""
PaceKeeper Qt - 태그 대화상자 (개선된 버전)
태그 관리 UI
"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)

from app.domain.category.category_service import CategoryService
from app.domain.tag.tag_entity import TagEntity
from app.domain.tag.tag_service import TagService
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.styles.update_dialogs import (apply_theme_change,
                                             set_object_names)


class TagDialog(QDialog):
    """태그 관리 대화상자 클래스 - 개선된 UI"""

    def __init__(
        self,
        parent=None,
        theme_manager=None,
    ):
        """
        태그 대화상자 초기화

        Args:
            parent: 부모 위젯
            controller_or_service: 메인 컨트롤러 또는 태그 서비스 인스턴스
            category_service: 카테고리 서비스 인스턴스
            theme_manager: 테마 관리자 인스턴스
        """
        super().__init__(parent)

        # 객체 이름 설정 - Qt 스타일시트 선택자용
        self.setObjectName("TagDialog")

        # 컨트롤러 또는 서비스 구분
        self.tag_service = TagService()
        self.category_service = CategoryService()

        # 단일 테마 관리자 인스턴스 사용
        self.theme_manager = theme_manager or AdvancedThemeManager.get_instance()
        self.current_tag = None
        self.categories = {}

        if self.theme_manager:
            self.theme_manager.register_widget(self)
            # 테마 변경 시그널 연결
            self.theme_manager.themeChanged.connect(self.on_theme_changed)

        # UI 초기화
        self.setupUI()

        # 다이얼로그의 모든 객체에 이름 설정
        set_object_names(self)

        # 초기 테마 적용
        if self.theme_manager:
            style_content = self.theme_manager.get_theme_style(
                self.theme_manager.get_current_theme()
            )
            if style_content:
                print(f"[DEBUG] 초기 테마 적용: {len(style_content)} 바이트")
                self.setStyleSheet(style_content)

                # 초기 테마 적용 후 갱신
                self.update()

        # 카테고리 및 태그 목록 로드
        self.loadCategories()
        self.loadTags()

        # 시그널 연결
        self.connectSignals()

    def setupUI(self):
        """태그 관리 UI 초기화 - 개선된 버전"""
        self.setWindowTitle("태그 관리")
        self.resize(600, 450)  # 더 넓게 조정

        # 메인 레이아웃
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # 왼쪽 패널 (태그 목록) - 카드 스타일 적용
        self.leftPanel = QWidget()
        self.leftPanel.setObjectName("leftPanel")
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(15, 15, 15, 15)
        self.leftLayout.setSpacing(10)

        # 태그 목록 헤더 - 더 강조된 스타일
        self.listLabel = QLabel("태그 목록")
        self.listLabel.setObjectName("listLabel")
        self.leftLayout.addWidget(self.listLabel)

        # 태그 목록 위젯 - 개선된 스타일
        self.tagList = QListWidget()
        self.tagList.setObjectName("tagList")
        self.tagList.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.leftLayout.addWidget(self.tagList)

        # 버튼 레이아웃 - 현대적인 버튼
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)

        # 추가, 삭제 버튼
        self.addButton = QPushButton("추가")
        self.addButton.setObjectName("addButton")
        self.addButton.setMinimumWidth(80)
        self.addButton.setMinimumHeight(32)

        self.removeButton = QPushButton("삭제")
        self.removeButton.setObjectName("removeButton")
        self.removeButton.setMinimumWidth(80)
        self.removeButton.setMinimumHeight(32)

        self.buttonLayout.addWidget(self.addButton)
        self.buttonLayout.addWidget(self.removeButton)
        self.leftLayout.addLayout(self.buttonLayout)

        # 오른쪽 패널 (태그 편집) - 카드 스타일 적용
        self.rightPanel = QWidget()
        self.rightPanel.setObjectName("rightPanel")
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setContentsMargins(20, 15, 20, 15)
        self.rightLayout.setSpacing(15)

        # 태그 편집 헤더
        self.editLabel = QLabel("태그 편집")
        self.editLabel.setObjectName("editLabel")
        self.rightLayout.addWidget(self.editLabel)

        # 태그 편집 폼 - 개선된 레이아웃
        self.editForm = QFormLayout()
        self.editForm.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.editForm.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.editForm.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.editForm.setContentsMargins(0, 10, 0, 0)
        self.editForm.setSpacing(15)

        # 이름 입력 - 개선된 입력 필드
        self.nameInput = QLineEdit()
        self.nameInput.setObjectName("nameInput")
        self.nameInput.setMinimumHeight(32)
        self.nameInput.setPlaceholderText("태그 이름 입력")
        self.editForm.addRow("이름:", self.nameInput)

        # 카테고리 콤보박스 - 개선된 드롭다운
        self.categoryComboBox = QComboBox()
        self.categoryComboBox.setObjectName("categoryComboBox")
        self.categoryComboBox.setMinimumHeight(32)
        self.categoryComboBox.setMinimumWidth(200)
        self.editForm.addRow("카테고리:", self.categoryComboBox)

        self.rightLayout.addLayout(self.editForm)

        # 저장, 취소 버튼 - 개선된 레이아웃 및 스타일
        self.actionLayout = QHBoxLayout()
        self.actionLayout.setContentsMargins(0, 15, 0, 0)
        self.actionLayout.setSpacing(10)

        self.actionLayout.addStretch(1)

        self.cancelButton = QPushButton("취소")
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setMinimumWidth(100)
        self.cancelButton.setMinimumHeight(36)

        self.saveButton = QPushButton("저장")
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setMinimumWidth(100)
        self.saveButton.setMinimumHeight(36)
        self.saveButton.setDefault(True)

        self.actionLayout.addWidget(self.cancelButton)
        self.actionLayout.addWidget(self.saveButton)
        self.rightLayout.addLayout(self.actionLayout)

        # 여백 추가
        self.rightLayout.addStretch(1)

        # 패널 분할 비율 설정 (왼쪽 : 오른쪽 = 1 : 1)
        self.main_layout.addWidget(self.leftPanel, 1)
        self.main_layout.addWidget(self.rightPanel, 1)

        # 초기 상태 설정
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
            print(f"[DEBUG] 카테고리 로드 실패: {e}")
            QMessageBox.warning(
                self, "오류", "카테고리 목록을 불러오는 중 오류가 발생했습니다."
            )

    def loadTags(self):
        """태그 목록 로드 및 카테고리 색상 적용"""
        self.tagList.clear()

        try:
            tags = self.tag_service.get_all_tags()

            for tag in tags:
                item = QListWidgetItem(f"#{tag.name}")
                item.setData(Qt.ItemDataRole.UserRole, tag)

                # 카테고리 색상 가져오기 및 안전한 접근
                category_info = self.categories.get(tag.category_id)
                color_hex = (
                    category_info["color"]
                    if category_info
                    else self.categories[None]["color"]
                )

                # 안전한 QColor 생성
                color = QColor(color_hex)
                if color.isValid():
                    item.setForeground(QBrush(color))

                self.tagList.addItem(item)
        except Exception as e:
            print(f"[DEBUG] 태그 로드 실패: {e}")
            QMessageBox.warning(
                self, "오류", "태그 목록을 불러오는 중 오류가 발생했습니다."
            )

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

            # 안전한 카테고리 접근
            if tag.category_id is not None and tag.category_id in self.categories:
                index = self.categoryComboBox.findData(tag.category_id)
                if index >= 0:
                    self.categoryComboBox.setCurrentIndex(index)
                else:
                    self.categoryComboBox.setCurrentIndex(0)
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
            try:
                self.tag_service.delete_tag(tag.id)

                self.loadTags()

                self.enableEditForm(False)
            except Exception as e:
                print(f"[DEBUG] 태그 삭제 실패: {e}")
                QMessageBox.warning(
                    self, "오류", "태그를 삭제하는 중 오류가 발생했습니다."
                )

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

        try:
            if self.current_tag:
                self.current_tag.name = name
                self.current_tag.category_id = selected_category_id

                if self.isNewTag():
                    self.tag_service.create_tag(
                        name=self.current_tag.name,
                        category_id=self.current_tag.category_id,
                    )
                else:
                    self.tag_service.update_tag(self.current_tag)

                self.loadTags()

                self.enableEditForm(False)
        except Exception as e:
            print(f"[DEBUG] 태그 저장 실패: {e}")
            QMessageBox.warning(self, "오류", "태그를 저장하는 중 오류가 발생했습니다.")

    @pyqtSlot()
    def onCancelEdit(self):
        """편집 취소 버튼 이벤트 핸들러"""
        self.enableEditForm(False)

        self.tagList.clearSelection()

    @pyqtSlot(str)
    def on_theme_changed(self, theme_name):
        """
        테마 변경 시그널을 처리하는 슬롯

        Args:
            theme_name: 변경된 테마 이름
        """
        print(f"[DEBUG] 테마 변경 시그널 수신: {theme_name}")

        # 테마 스타일 직접 적용
        if self.theme_manager:
            style_content = self.theme_manager.get_theme_style(theme_name)
            if style_content:
                print(f"[DEBUG] 테마 스타일 적용: {len(style_content)} 바이트")
                self.setStyleSheet(style_content)

                # 자식 위젯의 개별 스타일시트 제거
                for widget in self.findChildren(QWidget):
                    widget.setStyleSheet("")

                # 테마 적용 후 갱신
                self.update()

    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        if (
            hasattr(self, "theme_manager")
            and self.theme_manager is not None
            and hasattr(self, "on_theme_changed")
        ):
            # 테마 변경 시그널 연결 해제
            try:
                self.theme_manager.themeChanged.disconnect(self.on_theme_changed)
                self.theme_manager.unregister_widget(self)
            except (RuntimeError, TypeError):
                # disconnect 오류 무시(이미 연결 해제됐거나 유효하지 않은 경우)
                pass
        super().closeEvent(event)
