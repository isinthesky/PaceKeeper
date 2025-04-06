"""
PaceKeeper Qt - 태그 대화상자
태그 관리 UI
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, 
                             QLineEdit, QFormLayout, QColorDialog, QWidget, 
                             QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from app.domain.tag.tag_entity import TagEntity
from app.domain.tag.tag_service import TagService


class TagDialog(QDialog):
    """태그 관리 대화상자 클래스"""
    
    def __init__(self, parent=None, tag_service=None):
        """
        태그 대화상자 초기화
        
        Args:
            parent: 부모 위젯
            tag_service: 태그 서비스 인스턴스
        """
        super().__init__(parent)
        
        self.tag_service = tag_service or TagService()
        self.current_tag = None
        
        # UI 초기화
        self.setupUI()
        
        # 태그 목록 로드
        self.loadTags()
        
        # 시그널 연결
        self.connectSignals()
    
    def setupUI(self):
        """UI 초기화"""
        # 창 제목 및 크기 설정
        self.setWindowTitle("태그 관리")
        self.resize(450, 350)
        
        # 메인 레이아웃
        self.layout = QHBoxLayout(self)
        
        # 왼쪽 패널 (태그 목록)
        self.leftPanel = QWidget()
        self.leftLayout = QVBoxLayout(self.leftPanel)
        
        # 태그 목록 레이블
        self.listLabel = QLabel("태그 목록")
        self.leftLayout.addWidget(self.listLabel)
        
        # 태그 목록 위젯
        self.tagList = QListWidget()
        self.tagList.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.leftLayout.addWidget(self.tagList)
        
        # 버튼 레이아웃
        self.buttonLayout = QHBoxLayout()
        
        # 추가, 삭제 버튼
        self.addButton = QPushButton("추가")
        self.removeButton = QPushButton("삭제")
        
        self.buttonLayout.addWidget(self.addButton)
        self.buttonLayout.addWidget(self.removeButton)
        self.leftLayout.addLayout(self.buttonLayout)
        
        # 오른쪽 패널 (태그 편집)
        self.rightPanel = QWidget()
        self.rightLayout = QVBoxLayout(self.rightPanel)
        
        # 태그 편집 레이블
        self.editLabel = QLabel("태그 편집")
        self.rightLayout.addWidget(self.editLabel)
        
        # 태그 편집 폼
        self.editForm = QFormLayout()
        
        # 이름 입력
        self.nameInput = QLineEdit()
        self.editForm.addRow("이름:", self.nameInput)
        
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
        self.layout.addWidget(self.rightPanel, 1)
        
        # 초기 상태 설정
        self.enableEditForm(False)
    
    def connectSignals(self):
        """시그널 연결"""
        # 태그 목록 관련
        self.tagList.currentItemChanged.connect(self.onTagSelected)
        
        # 버튼 관련
        self.addButton.clicked.connect(self.onAddTag)
        self.removeButton.clicked.connect(self.onRemoveTag)
        self.colorButton.clicked.connect(self.onSelectColor)
        self.saveButton.clicked.connect(self.onSaveTag)
        self.cancelButton.clicked.connect(self.onCancelEdit)
    
    def loadTags(self):
        """태그 목록 로드"""
        # 목록 초기화
        self.tagList.clear()
        
        # 태그 조회
        tags = self.tag_service.get_all_tags()
        
        # 목록에 추가
        for tag in tags:
            item = QListWidgetItem(f"#{tag.name}")
            item.setData(Qt.ItemDataRole.UserRole, tag)
            
            # 색상 적용
            color = QColor(tag.color)
            item.setForeground(QBrush(color))
            
            self.tagList.addItem(item)
    
    def enableEditForm(self, enabled):
        """
        편집 폼 활성화 상태 변경
        
        Args:
            enabled: 활성화 여부
        """
        self.nameInput.setEnabled(enabled)
        self.colorButton.setEnabled(enabled)
        self.saveButton.setEnabled(enabled)
        self.cancelButton.setEnabled(enabled)
        
        if not enabled:
            self.nameInput.clear()
            self.colorPreview.setStyleSheet("")
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
            # 태그 데이터 가져오기
            tag = current.data(Qt.ItemDataRole.UserRole)
            
            # 현재 태그 설정
            self.current_tag = tag
            
            # 폼에 데이터 표시
            self.nameInput.setText(tag.name)
            self.colorPreview.setStyleSheet(f"background-color: {tag.color};")
            
            # 폼 활성화
            self.enableEditForm(True)
        else:
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onAddTag(self):
        """태그 추가 버튼 이벤트 핸들러"""
        # 새 태그 생성
        new_tag = Tag(name="new_tag", color="#4a86e8")
        
        # 현재 태그로 설정
        self.current_tag = new_tag
        
        # 폼에 데이터 표시
        self.nameInput.setText(new_tag.name)
        self.colorPreview.setStyleSheet(f"background-color: {new_tag.color};")
        
        # 폼 활성화
        self.enableEditForm(True)
        
        # 포커스 설정
        self.nameInput.setFocus()
        self.nameInput.selectAll()
    
    @pyqtSlot()
    def onRemoveTag(self):
        """태그 삭제 버튼 이벤트 핸들러"""
        # 현재 선택된 항목 확인
        current_item = self.tagList.currentItem()
        if not current_item:
            return
        
        # 태그 데이터 가져오기
        tag = current_item.data(Qt.ItemDataRole.UserRole)
        
        # 확인 대화상자 표시
        reply = QMessageBox.question(
            self, 
            "태그 삭제", 
            f"'#{tag.name}' 태그를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 태그 삭제
            self.tag_service.delete_tag(tag.id)
            
            # 목록 다시 로드
            self.loadTags()
            
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onSelectColor(self):
        """색상 선택 버튼 이벤트 핸들러"""
        # 현재 색상 가져오기
        current_color = QColor(self.current_tag.color) if self.current_tag else QColor("#4a86e8")
        
        # 색상 대화상자 표시
        color = QColorDialog.getColor(current_color, self, "색상 선택")
        
        # 색상이 유효하면 적용
        if color.isValid():
            self.colorPreview.setStyleSheet(f"background-color: {color.name()};")
    
    @pyqtSlot()
    def onSaveTag(self):
        """태그 저장 버튼 이벤트 핸들러"""
        # 입력 유효성 검사
        name = self.nameInput.text().strip()
        # 태그 이름에서 # 제거
        if name.startswith('#'):
            name = name[1:]
        
        if not name:
            QMessageBox.warning(self, "입력 오류", "태그 이름을 입력하세요.")
            self.nameInput.setFocus()
            return
        
        # 색상 가져오기
        color_style = self.colorPreview.styleSheet()
        color = "#4a86e8"  # 기본 색상
        if "background-color:" in color_style:
            # 배경색 추출
            parts = color_style.split("background-color:")[1].strip()
            color = parts.rstrip(";")
        
        # 태그 업데이트
        if self.current_tag:
            self.current_tag.name = name
            self.current_tag.color = color
            
            # 새 태그인 경우 생성, 기존 태그인 경우 업데이트
            if self.isNewTag():
                self.tag_service.create_tag(
                    name=self.current_tag.name,
                    color=self.current_tag.color
                )
            else:
                self.tag_service.update_tag(self.current_tag)
            
            # 목록 다시 로드
            self.loadTags()
            
            # 폼 비활성화
            self.enableEditForm(False)
    
    @pyqtSlot()
    def onCancelEdit(self):
        """편집 취소 버튼 이벤트 핸들러"""
        # 폼 비활성화
        self.enableEditForm(False)
        
        # 현재 선택된 항목 선택 해제
        self.tagList.clearSelection()
