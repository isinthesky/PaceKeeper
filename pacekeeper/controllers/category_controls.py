
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QColorDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pacekeeper.interfaces.services.i_category_service import ICategoryService


class CategoryControlsPanel(QWidget):
    """
    CategoryControlsPanel: 카테고리 목록을 보여주고
    새로운 카테고리 생성, 선택된 카테고리 수정 및 삭제 기능을 제공하는 패널.
    """
    def __init__(self, parent=None, category_service: ICategoryService | None = None):
        super().__init__(parent)
        # 의존성 주입을 위해 기본값으로 None을 받고, 실제 주입은 외부에서 처리
        self.service = category_service
        if self.service:
            self.InitUI()
            self.update_category_list()


    def InitUI(self):
        main_layout = QVBoxLayout()

        # 카테고리 목록을 표시할 ListWidget 생성
        self.list_widget = QListWidget(self)
        main_layout.addWidget(self.list_widget)

        # 카테고리 정보 입력용 폼 (이름, 설명, 색상)
        form_layout = QGridLayout()
        name_label = QLabel("이름:", self)
        self.name_text = QLineEdit(self)
        description_label = QLabel("설명:", self)
        self.description_text = QLineEdit(self)
        color_label = QLabel("색상:", self)
        self.color_button = QPushButton(self)
        self.color_button.setFixedSize(30, 30)
        self.color_button.setStyleSheet("background-color: #FFFFFF;")
        self.color_button.clicked.connect(self.on_color_pick)
        self.current_color = "#FFFFFF"

        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_text, 0, 1)
        form_layout.addWidget(description_label, 1, 0)
        form_layout.addWidget(self.description_text, 1, 1)
        form_layout.addWidget(color_label, 2, 0)
        form_layout.addWidget(self.color_button, 2, 1)

        main_layout.addLayout(form_layout)

        # 버튼 영역: 생성, 수정, 삭제
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("생성", self)
        self.modify_btn = QPushButton("수정", self)
        self.delete_btn = QPushButton("삭제", self)
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.modify_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # 이벤트 연결
        self.create_btn.clicked.connect(self.on_create)
        self.modify_btn.clicked.connect(self.on_modify)
        self.delete_btn.clicked.connect(self.on_delete)
        self.list_widget.itemClicked.connect(self.on_item_selected)

    def on_color_pick(self):
        """색상 선택 다이얼로그 표시"""
        color = QColorDialog.getColor(QColor(self.current_color), self, "색상 선택")
        if color.isValid():
            self.current_color = color.name()
            self.color_button.setStyleSheet(f"background-color: {self.current_color};")

    def update_category_list(self):
        """카테고리 목록을 서비스로부터 조회하여 ListWidget에 업데이트합니다."""
        self.list_widget.clear()
        categories = self.service.get_categories()
        for category in categories:
            item = QListWidgetItem(f"{category.id}: {category.name} - {category.description}")
            item.setData(Qt.UserRole, category)
            self.list_widget.addItem(item)

    def on_create(self):
        """새 카테고리를 생성합니다."""
        name = self.name_text.text().strip()
        description = self.description_text.text().strip()
        color = self.current_color
        if not name:
            QMessageBox.critical(self, "오류", "이름을 입력하세요.")
            return
        try:
            self.service.create_category(name, description, color)
            QMessageBox.information(self, "정보", f"카테고리 생성 완료 {name}")
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"카테고리 생성 실패 {e}")

    def on_modify(self):
        """선택한 카테고리의 정보를 수정합니다."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "알림", "수정할 카테고리를 선택하세요.")
            return

        selected_category = selected_items[0].data(Qt.UserRole)
        category_id = selected_category.id

        new_name = self.name_text.text().strip()
        new_description = self.description_text.text().strip()
        new_color = self.current_color

        if not new_name:
            QMessageBox.critical(self, "오류", "이름을 입력하세요.")
            return
        try:
            self.service.update_category(category_id, new_name, new_description, new_color)
            QMessageBox.information(self, "정보", "카테고리 수정 완료")
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"카테고리 수정 실패 {e}")

    def on_delete(self):
        """선택한 카테고리를 삭제(soft delete)합니다."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "알림", "삭제할 카테고리를 선택하세요.")
            return

        selected_category = selected_items[0].data(Qt.UserRole)
        category_id = selected_category.id

        answer = QMessageBox.question(self, "확인", "선택한 카테고리를 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        try:
            self.service.delete_category(category_id)
            QMessageBox.information(self, "정보", "카테고리 삭제 완료")
            self.clear_form()
            self.update_category_list()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"카테고리 삭제 실패 {e}")

    def on_item_selected(self, item):
        """
        목록에서 항목이 선택되면 해당 카테고리의 이름, 설명 및 색상을 입력 폼에 채웁니다.
        """
        selected_category = item.data(Qt.UserRole)

        self.name_text.setText(selected_category.name)
        self.description_text.setText(selected_category.description)

        # 저장된 색상 값이 올바른 형식인지 확인 후 색상 박스 업데이트
        color_text = selected_category.color
        if color_text and color_text.startswith("#") and len(color_text) == 7:
            try:
                self.current_color = color_text
                self.color_button.setStyleSheet(f"background-color: {self.current_color};")
            except Exception:
                self.current_color = "#FFFFFF"
                self.color_button.setStyleSheet("background-color: #FFFFFF;")
        else:
            self.current_color = "#FFFFFF"
            self.color_button.setStyleSheet("background-color: #FFFFFF;")

    def clear_form(self):
        """입력 폼 초기화 및 리스트 선택 해제."""
        self.name_text.setText("")
        self.description_text.setText("")
        self.current_color = "#FFFFFF"
        self.color_button.setStyleSheet("background-color: #FFFFFF;")
        self.list_widget.clearSelection()

class TagButtonsPanel(QWidget):
    """태그 버튼들을 관리하는 패널"""
    tag_selected = pyqtSignal(dict)

    def __init__(self, parent=None, on_tag_selected=None, category_service: ICategoryService | None = None):
        super().__init__(parent)
        self.on_tag_selected = on_tag_selected
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        # CategoryService는 의존성 주입을 통해 전달받습니다
        self.service = category_service
        self.selected_tag = None


    def update_tags(self, tags:list[dict]):
        """
        태그 버튼 업데이트 메서드.
        """
        if not self.service:
            return

        # 기존 버튼 제거
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        categories = self.service.get_all_categories()
        color_set = {category.id: category for category in categories}

        for tag in tags:
            if tag:
                # 명시적으로 문자열 변환하여 인코딩 보장
                tag_name = str(tag["name"])
                btn = QPushButton(tag_name, self)

                if self.on_tag_selected:
                    btn.clicked.connect(lambda checked, t=tag: self.on_tag_selected(t))
                else:
                    btn.clicked.connect(lambda checked, t=tag: self.tag_selected.emit(t))

                category = color_set.get(tag["category_id"])
                if category:
                    btn.setStyleSheet(f"background-color: {category.color};")

                self.layout.addWidget(btn)

        self.update()
