# views/category_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeyEvent

from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.category_controls import CategoryControlsPanel, TagButtonsPanel
from pacekeeper.services.tag_service import TagService
from pacekeeper.services.category_service import CategoryService
from pacekeeper.consts.labels import load_language_resource
from icecream import ic

lang_res = load_language_resource(ConfigController().get_language())

class CategoryDialog(QDialog):
    def __init__(self, parent, config_controller):
        super().__init__(parent)
        self.setWindowTitle(lang_res.base_labels['CATEGORY'])
        self.setFixedSize(660, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.config = config_controller
        self.tag_service = TagService()
        self.category_service = CategoryService()
        self.selected_tag = None
        self.InitUI()
        self.center_on_screen()

    def InitUI(self):
        main_layout = QVBoxLayout(self)

        # 타이틀 레이블 추가
        title_label = QLabel(lang_res.base_labels['CATEGORY'])
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 좌우 영역용 Horizontal Layout 생성
        content_layout = QHBoxLayout()

        # CategoryControlsPanel: 왼쪽에 배치
        controls_panel = CategoryControlsPanel(self)
        content_layout.addWidget(controls_panel, 1)

        # TagButtonsPanel: 오른쪽에 배치
        self.tag_panel = TagButtonsPanel(self)
        self.tag_panel.tag_selected.connect(self.add_tag_to_input)
        content_layout.addWidget(self.tag_panel, 1)

        # 좌우 영역을 main_layout에 추가
        main_layout.addLayout(content_layout, 1)

        # 닫기 버튼 영역 추가
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        
        # 태그 목록 업데이트
        tags = self.tag_service.get_tags()
        ic("tags", tags)
        self.tag_panel.update_tags(tags)
        
    def add_tag_to_input(self, tag):
        ic("add_tag_to_input", tag)
        self.selected_tag = tag
        
    def keyPressEvent(self, event):
        """
        다이얼로그에서 키 입력 이벤트를 처리하는 핸들러입니다.
        """
        keycode = event.key()
        ic("키 입력 이벤트:", keycode)
        
        # 숫자 키 0-9 확인 (Qt.Key_0 ~ Qt.Key_9)
        if Qt.Key_0 <= keycode <= Qt.Key_9:
            select_number = keycode - Qt.Key_0
            
            if not self.selected_tag:
                ic("selected_tag가 없습니다.")
                super().keyPressEvent(event)
                return
                
            ic("숫자 키 입력", select_number)
            ic("selected_tag", self.selected_tag)
            
            category = self.category_service.get_category(select_number)
            ic("category", category)
            
            if not category:
                ic("category가 없습니다.")
                super().keyPressEvent(event)
                return
            
            tag = self.tag_service.get_tag(self.selected_tag["id"])
            ic("tag", tag)
            
            tag.category_id = category.id
            
            updated_tag = self.tag_service.update_tag(tag)
            ic("updated_tag", updated_tag)
            
            # 태그 업데이트 후, 최신 태그 목록을 불러와 tag 버튼 패널을 갱신합니다.
            tags = self.tag_service.get_tags()
            self.tag_panel.update_tags(tags)
        
        super().keyPressEvent(event)  # 이벤트를 상위 클래스로 전달
        
    def center_on_screen(self):
        """화면 중앙에 다이얼로그를 배치합니다."""
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
