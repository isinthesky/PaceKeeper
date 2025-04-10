"""
PaceKeeper Qt - 카테고리 대화상자 (개선된 버전)
카테고리 관리 UI
"""

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (QApplication, QColorDialog, QDialog, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)

from app.domain.category.category_entity import CategoryEntity
from app.domain.category.category_service import CategoryService
from app.views.styles.advanced_theme_manager import AdvancedThemeManager
from app.views.styles.update_dialogs import (apply_theme_change,
                                             set_object_names)


class CategoryDialog(QDialog):
    """카테고리 관리 대화상자 클래스 - 개선된 UI"""

    def __init__(self, parent=None, theme_manager=None):
        """
        카테고리 대화상자 초기화

        Args:
            parent: 부모 위젯
            controller_or_service: 메인 컨트롤러 또는 카테고리 서비스 인스턴스
            theme_manager: 테마 관리자 인스턴스
        """
        super().__init__(parent)

        # 객체 이름 설정 - Qt 스타일시트 선택자용
        self.setObjectName("CategoryDialog")

        # 컨트롤러 또는 서비스 구분
        from app.controllers.main_controller import MainController

        self.category_service = CategoryService()

        # 단일 테마 관리자 인스턴스 사용
        self.theme_manager = theme_manager or AdvancedThemeManager.get_instance()
        self.current_category = None

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

        # 카테고리 목록 로드
        self.loadCategories()

        # 시그널 연결
        self.connectSignals()

    def setupUI(self):
        """카테고리 관리 UI 초기화 - 개선된 버전"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("카테고리 관리")
        self.resize(600, 450)  # 더 넓게 조정

        # 메인 레이아웃
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)  # 패널 간 간격 증가

        # 왼쪽 패널 (카테고리 목록) - 카드 스타일 적용
        self.leftPanel = QWidget()
        self.leftPanel.setObjectName("leftPanel")
        self.leftLayout = QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(15, 15, 15, 15)
        self.leftLayout.setSpacing(10)

        # 카테고리 목록 헤더 - 더 강조된 스타일
        self.listLabel = QLabel("카테고리 목록")
        self.listLabel.setObjectName("listLabel")
        self.leftLayout.addWidget(self.listLabel)

        # 카테고리 목록 위젯 - 개선된 스타일
        self.categoryList = QListWidget()
        self.categoryList.setObjectName("categoryList")
        self.categoryList.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.leftLayout.addWidget(self.categoryList)

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

        # 오른쪽 패널 (카테고리 편집) - 카드 스타일 적용
        self.rightPanel = QWidget()
        self.rightPanel.setObjectName("rightPanel")
        self.rightLayout = QVBoxLayout(self.rightPanel)
        self.rightLayout.setContentsMargins(20, 15, 20, 15)
        self.rightLayout.setSpacing(15)

        # 카테고리 편집 헤더
        self.editLabel = QLabel("카테고리 편집")
        self.editLabel.setObjectName("editLabel")
        self.rightLayout.addWidget(self.editLabel)

        # 카테고리 편집 폼 - 개선된 레이아웃
        self.editForm = QFormLayout()
        self.editForm.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.editForm.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.editForm.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.editForm.setContentsMargins(0, 10, 0, 0)
        self.editForm.setSpacing(15)  # 폼 항목 간 간격 증가

        # 이름 입력 - 개선된 입력 필드
        self.nameInput = QLineEdit()
        self.nameInput.setObjectName("nameInput")
        self.nameInput.setMinimumHeight(32)
        self.editForm.addRow("이름:", self.nameInput)

        # 설명 입력
        self.descriptionInput = QLineEdit()
        self.descriptionInput.setObjectName("descriptionInput")
        self.descriptionInput.setMinimumHeight(32)
        self.editForm.addRow("설명:", self.descriptionInput)

        # 색상 선택 - 개선된 UI
        self.colorLayout = QHBoxLayout()
        self.colorLayout.setSpacing(10)

        self.colorPreview = QFrame()
        self.colorPreview.setObjectName("colorPreview")
        self.colorPreview.setFixedSize(40, 32)
        self.colorPreview.setFrameShape(QFrame.Shape.Box)

        self.colorButton = QPushButton("색상 선택")
        self.colorButton.setObjectName("colorButton")
        self.colorButton.setMinimumHeight(32)

        self.colorLayout.addWidget(self.colorPreview)
        self.colorLayout.addWidget(self.colorButton)
        self.editForm.addRow("색상:", self.colorLayout)

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

        # 패널 분할 비율 설정 (왼쪽 : 오른쪽 = 2 : 3)
        self.main_layout.addWidget(self.leftPanel, 2)
        self.main_layout.addWidget(self.rightPanel, 3)

        # 초기 상태 설정
        self.enableEditForm(False)

    def connectSignals(self):
        """시그널 연결"""
        # 카테고리 목록 관련
        self.categoryList.currentItemChanged.connect(self.onCategorySelected)

        # 버튼 관련
        self.addButton.clicked.connect(self.onAddCategory)
        self.removeButton.clicked.connect(self.onRemoveCategory)
        self.colorButton.clicked.connect(self.onSelectColor)
        self.saveButton.clicked.connect(self.onSaveCategory)
        self.cancelButton.clicked.connect(self.onCancelEdit)

    def loadCategories(self):
        """카테고리 목록 로드"""
        # 목록 초기화
        self.categoryList.clear()

        try:
            # 카테고리 조회
            categories = self.category_service.get_all_categories()

            # 목록에 추가
            for category in categories:
                item = QListWidgetItem(category.name)
                item.setData(Qt.ItemDataRole.UserRole, category)

                # 색상 적용
                color = QColor(category.color)
                item.setForeground(QBrush(color))

                self.categoryList.addItem(item)
        except Exception as e:
            print(f"[DEBUG] 카테고리 로드 실패: {e}")
            QMessageBox.warning(
                self, "오류", "카테고리 목록을 불러오는 중 오류가 발생했습니다."
            )

    def enableEditForm(self, enabled):
        """
        편집 폼 활성화 상태 변경

        Args:
            enabled: 활성화 여부
        """
        self.nameInput.setEnabled(enabled)
        self.descriptionInput.setEnabled(enabled)
        self.colorButton.setEnabled(enabled)
        self.saveButton.setEnabled(enabled)
        self.cancelButton.setEnabled(enabled)

        if not enabled:
            self.nameInput.clear()
            self.descriptionInput.clear()
            self.colorPreview.setStyleSheet("")
            self.current_category = None

    def isNewCategory(self):
        """
        현재 편집 중인 카테고리가 새 카테고리인지 확인

        Returns:
            새 카테고리 여부
        """
        return self.current_category is not None and self.current_category.id is None

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def onCategorySelected(self, current, previous):
        """
        카테고리 선택 이벤트 핸들러

        Args:
            current: 현재 선택된 항목
            previous: 이전 선택된 항목
        """
        if current:
            # 카테고리 데이터 가져오기
            category = current.data(Qt.ItemDataRole.UserRole)

            # 현재 카테고리 설정
            self.current_category = category

            # 폼에 데이터 표시
            self.nameInput.setText(category.name)
            self.descriptionInput.setText(category.description)
            self.colorPreview.setStyleSheet(
                f"background-color: {category.color}; border-radius: 4px; border: 1px solid palette(mid);"
            )

            # 폼 활성화
            self.enableEditForm(True)
        else:
            # 폼 비활성화
            self.enableEditForm(False)

    @pyqtSlot()
    def onAddCategory(self):
        """카테고리 추가 버튼 이벤트 핸들러"""
        # 새 카테고리 생성
        new_category = CategoryEntity(id=None, name="새 카테고리", color="#4a86e8")

        # 현재 카테고리로 설정
        self.current_category = new_category

        # 폼에 데이터 표시
        self.nameInput.setText(new_category.name)
        self.descriptionInput.clear()
        self.colorPreview.setStyleSheet(
            f"background-color: {new_category.color}; border-radius: 4px; border: 1px solid palette(mid);"
        )

        # 폼 활성화
        self.enableEditForm(True)

        # 포커스 설정
        self.nameInput.setFocus()
        self.nameInput.selectAll()

    @pyqtSlot()
    def onRemoveCategory(self):
        """카테고리 삭제 버튼 이벤트 핸들러"""
        # 현재 선택된 항목 확인
        current_item = self.categoryList.currentItem()
        if not current_item:
            return

        # 카테고리 데이터 가져오기
        category = current_item.data(Qt.ItemDataRole.UserRole)

        # 확인 대화상자 표시
        reply = QMessageBox.question(
            self,
            "카테고리 삭제",
            f"'{category.name}' 카테고리를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 카테고리 삭제
                self.category_service.delete_category(category.id)

                # 목록 다시 로드
                self.loadCategories()

                # 폼 비활성화
                self.enableEditForm(False)
            except Exception as e:
                print(f"[DEBUG] 카테고리 삭제 실패: {e}")
                QMessageBox.warning(
                    self, "오류", "카테고리를 삭제하는 중 오류가 발생했습니다."
                )

    @pyqtSlot()
    def onSelectColor(self):
        """색상 선택 버튼 이벤트 핸들러"""
        # 현재 색상 가져오기
        current_color = (
            QColor(self.current_category.color)
            if self.current_category
            else QColor("#4a86e8")
        )

        # 색상 대화상자 표시
        color = QColorDialog.getColor(current_color, self, "색상 선택")

        # 색상이 유효하면 적용 - 타입 체크 에러 수정
        if color.isValid():
            # 색상 이름 변수에 저장 후 사용
            color_name = color.name()
            self.colorPreview.setStyleSheet(
                f"background-color: {color_name}; border-radius: 4px; border: 1px solid palette(mid);"
            )

    @pyqtSlot()
    def onSaveCategory(self):
        """카테고리 저장 버튼 이벤트 핸들러"""
        # 입력 유효성 검사
        name = self.nameInput.text().strip()
        if not name:
            QMessageBox.warning(self, "입력 오류", "카테고리 이름을 입력하세요.")
            self.nameInput.setFocus()
            return

        # 색상 가져오기
        color_style = self.colorPreview.styleSheet()
        color = "#4a86e8"  # 기본 색상
        if "background-color:" in color_style:
            # 배경색 추출
            parts = color_style.split("background-color:")[1].strip()
            color = parts.split(";")[0].strip()

        try:
            # 카테고리 업데이트
            if self.current_category:
                self.current_category.name = name
                self.current_category.description = self.descriptionInput.text().strip()
                self.current_category.color = color

                # 새 카테고리인 경우 생성, 기존 카테고리인 경우 업데이트
                if self.isNewCategory():
                    self.category_service.create_category(
                        name=self.current_category.name,
                        description=self.current_category.description,
                        color=self.current_category.color,
                    )
                else:
                    self.category_service.update_category(self.current_category)

                # 목록 다시 로드
                self.loadCategories()

                # 폼 비활성화
                self.enableEditForm(False)
        except Exception as e:
            print(f"[DEBUG] 카테고리 저장 실패: {e}")
            QMessageBox.warning(
                self, "오류", "카테고리를 저장하는 중 오류가 발생했습니다."
            )

    @pyqtSlot()
    def onCancelEdit(self):
        """편집 취소 버튼 이벤트 핸들러"""
        # 폼 비활성화
        self.enableEditForm(False)

        # 현재 선택된 항목 선택 해제
        self.categoryList.clearSelection()

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
