"""
PaceKeeper Qt - 카테고리 대화상자
카테고리 관리 UI
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QLineEdit, QFormLayout, QColorDialog, QWidget, 
                             QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from app.domain.category.category_entity import CategoryEntity
from app.domain.category.category_service import CategoryService


class CategoryDialog(QDialog):
    """카테고리 관리 대화상자 클래스"""
    
    def __init__(self, parent=None, category_service=None):
        """
        카테고리 대화상자 초기화
        
        Args:
            parent: 부모 위젯
            category_service: 카테고리 서비스 인스턴스
        """
        super().__init__(parent)
        
        self.category_service = category_service or CategoryService()
        self.current_category = None
        
        # UI 초기화
        self.setupUI()
        
        # 카테고리 목록 로드
        self.loadCategories()
        
        # 시그널 연결
        self.connectSignals()
    
    def setupUI(self):
        """UI 초기화"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("카테고리 관리")
        self.resize(500, 400)
        
        # 메인 레이아웃
        self.layout = QHBoxLayout(self)
        
        # 왼쪽 패널 (카테고리 목록)
        self.leftPanel = QWidget()
        self.leftLayout = QVBoxLayout(self.leftPanel)
        
        # 카테고리 목록 레이블
        self.listLabel = QLabel("카테고리 목록")
        self.leftLayout.addWidget(self.listLabel)
        
        # 카테고리 목록 위젯
        self.categoryList = QListWidget()
        self.categoryList.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.leftLayout.addWidget(self.categoryList)
        
        # 버튼 레이아웃
        self.buttonLayout = QHBoxLayout()
        
        # 추가, 삭제 버튼
        self.addButton = QPushButton("추가")
        self.removeButton = QPushButton("삭제")
        
        self.buttonLayout.addWidget(self.addButton)
        self.buttonLayout.addWidget(self.removeButton)
        self.leftLayout.addLayout(self.buttonLayout)
        
        # 오른쪽 패널 (카테고리 편집)
        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout(self.rightPanel)
        
        # 카테고리 편집 레이블
        self.editLabel = QLabel("카테고리 편집")
        self.rightLayout.addWidget(self.editLabel)
        
        # 카테고리 편집 폼
        self.editForm = QFormLayout()
        
        # 이름 입력
        self.nameInput = QLineEdit()
        self.editForm.addRow("이름:", self.nameInput)
        
        # 설명 입력
        self.descriptionInput = QLineEdit()
        self.editForm.addRow("설명:", self.descriptionInput)
        
        # 색상 선택
        self.colorLayout = QHBoxLayout()
        self.colorPreview = QFrame()
        self.colorPreview.setFixedSize(30, 30)
        self.colorPreview.setFrameShape(QFrame.Shape.Box)
        self.colorButton = QPushButton("색상 선택")
        self.colorLayout.addWidget(self.colorPreview)
        self.colorLayout.addWidget(self.colorButton)
        self.editForm.addRow("색상:", self.colorLayout)
        
        self.rightLayout.addLayout(self.editForm)
        
        # 저장, 취소 버튼
        self.actionLayout = QHBoxLayout()
        self.saveButton = QPushButton("저장")
        self.cancelButton = QPushButton("취소")
        self.actionLayout.addWidget(self.saveButton)
        self.actionLayout.addWidget(self.cancelButton)
        self.rightLayout.addLayout(self.actionLayout)
        
        # 여백 추가
        self.rightLayout.addStretch(1)
        
        # 패널 분할 비율 설정
        self.layout.addWidget(self.leftPanel, 1)
        self.layout.addWidget(self.rightPanel, 2)
        
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
            self.colorPreview.setStyleSheet(f"background-color: {category.color};")
            
            # 폼 활성화
            self.enableEditForm(True)
        else:
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onAddCategory(self):
        """카테고리 추가 버튼 이벤트 핸들러"""
        # 새 카테고리 생성
        new_category = Category(name="새 카테고리", color="#4a86e8")
        
        # 현재 카테고리로 설정
        self.current_category = new_category
        
        # 폼에 데이터 표시
        self.nameInput.setText(new_category.name)
        self.descriptionInput.setText(new_category.description)
        self.colorPreview.setStyleSheet(f"background-color: {new_category.color};")
        
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
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 카테고리 삭제
            self.category_service.delete_category(category.id)
            
            # 목록 다시 로드
            self.loadCategories()
            
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onSelectColor(self):
        """색상 선택 버튼 이벤트 핸들러"""
        # 현재 색상 가져오기
        current_color = QColor(self.current_category.color) if self.current_category else QColor("#4a86e8")
        
        # 색상 대화상자 표시
        color = QColorDialog.getColor(current_color, self, "색상 선택")
        
        # 색상이 유효하면 적용
        if color.isValid():
            self.colorPreview.setStyleSheet(f"background-color: {color.name()};")
    
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
            color = parts.rstrip(";")
        
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
                    color=self.current_category.color
                )
            else:
                self.category_service.update_category(self.current_category)
            
            # 목록 다시 로드
            self.loadCategories()
            
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onCancelEdit(self):
        """편집 취소 버튼 이벤트 핸들러"""
        # 폼 비활성화
        self.enableEditForm(False)
        
        # 현재 선택된 항목 선택 해제
        self.categoryList.clearSelection()
