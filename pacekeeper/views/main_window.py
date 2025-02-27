# views/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QAction, QMenu, QMessageBox,
    QSizePolicy, QSpacerItem, QFrame, QShortcut
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QKeySequence

from pacekeeper.views.controls import (
    TimerLabel, RecentLogsControl, TagButtonsPanel, TextInputPanel
)
from pacekeeper.views.settings_dialog import SettingsDialog
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.views.category_dialog import CategoryDialog
from pacekeeper.views.log_dialog import LogDialog
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.consts.labels import load_language_resource


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    def __init__(self, main_controller, config_controller):
        super().__init__()
        
        self.main_ctrl = main_controller
        self.config_ctrl = config_controller
        self.lang_res = load_language_resource(config_controller.get_language())
        
        self.init_ui()
        self.init_menu()
        self.init_events()
        
        # 윈도우 설정
        self.setWindowTitle("PaceKeeper")
        self.setMinimumSize(600, 500)
        self.center_on_screen()
        
    def init_ui(self):
        """UI 구성요소 초기화"""
        # 중앙 위젯 생성
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 타이머 섹션
        timer_layout = QVBoxLayout()
        timer_layout.setAlignment(Qt.AlignCenter)
        
        # 타이머 레이블
        self.timer_label = TimerLabel(central_widget, "25:00")
        timer_layout.addWidget(self.timer_label, 0, Qt.AlignCenter)
        
        # 타이머 컨트롤 버튼 레이아웃
        timer_buttons_layout = QHBoxLayout()
        timer_buttons_layout.setAlignment(Qt.AlignCenter)
        timer_buttons_layout.setSpacing(10)
        
        # 시작 버튼
        self.start_button = QPushButton(self.lang_res.button_labels['START'], central_widget)
        self.start_button.setMinimumSize(100, 40)
        self.start_button.setToolTip(f"{self.lang_res.button_labels['START']} (F5)")
        timer_buttons_layout.addWidget(self.start_button)
        
        # 일시정지 버튼
        self.pause_button = QPushButton(self.lang_res.button_labels['PAUSE'], central_widget)
        self.pause_button.setMinimumSize(100, 40)
        self.pause_button.setEnabled(False)
        self.pause_button.setToolTip(f"{self.lang_res.button_labels['PAUSE']} (F6)")
        timer_buttons_layout.addWidget(self.pause_button)
        
        # 중지 버튼
        self.stop_button = QPushButton(self.lang_res.button_labels['STOP'], central_widget)
        self.stop_button.setMinimumSize(100, 40)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip(f"{self.lang_res.button_labels['STOP']} (F7)")
        timer_buttons_layout.addWidget(self.stop_button)
        
        timer_layout.addLayout(timer_buttons_layout)
        main_layout.addLayout(timer_layout)
        
        # 구분선
        line = QFrame(central_widget)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 태그 버튼 패널
        self.tag_buttons_panel = TagButtonsPanel(
            central_widget, 
            self.on_tag_selected
        )
        main_layout.addWidget(self.tag_buttons_panel)
        
        # 텍스트 입력 패널
        self.text_input_panel = TextInputPanel(
            central_widget,
            self.lang_res.messages['TASK_DESCRIPTION'],
            self.on_text_changed
        )
        main_layout.addWidget(self.text_input_panel)
        
        # 최근 로그 컨트롤
        self.recent_logs_control = RecentLogsControl(
            central_widget, 
            self.config_ctrl,
            self.on_log_double_clicked
        )
        main_layout.addWidget(self.recent_logs_control, 1)
        
        # 상태 표시줄
        self.statusBar().showMessage(self.lang_res.messages['READY'])
        
    def init_menu(self):
        """메뉴바 초기화"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu(self.lang_res.menu_labels['FILE'])
        
        # 설정 액션
        settings_action = QAction(self.lang_res.menu_labels['SETTINGS'], self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.on_settings)
        file_menu.addAction(settings_action)
        
        # 카테고리 액션
        category_action = QAction(self.lang_res.menu_labels['CATEGORY'], self)
        category_action.setShortcut(QKeySequence("Ctrl+C"))
        category_action.triggered.connect(self.on_category)
        file_menu.addAction(category_action)
        
        # 로그 액션
        logs_action = QAction(self.lang_res.menu_labels['LOGS'], self)
        logs_action.setShortcut(QKeySequence("Ctrl+L"))
        logs_action.triggered.connect(self.on_logs)
        file_menu.addAction(logs_action)
        
        # 구분선
        file_menu.addSeparator()
        
        # 종료 액션
        exit_action = QAction(self.lang_res.menu_labels['EXIT'], self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu(self.lang_res.menu_labels['HELP'])
        
        # 정보 액션
        about_action = QAction(self.lang_res.menu_labels['ABOUT'], self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def init_events(self):
        """이벤트 연결"""
        # 타이머 버튼 이벤트
        self.start_button.clicked.connect(self.on_start)
        self.pause_button.clicked.connect(self.on_pause)
        self.stop_button.clicked.connect(self.on_stop)
        
        # 단축키 설정
        self.init_shortcuts()
        
    def init_shortcuts(self):
        """단축키 초기화"""
        # 타이머 제어 단축키
        self.shortcut_start = QShortcut(QKeySequence("F5"), self)
        self.shortcut_start.activated.connect(self.on_shortcut_start)
        
        self.shortcut_pause = QShortcut(QKeySequence("F6"), self)
        self.shortcut_pause.activated.connect(self.on_shortcut_pause)
        
        self.shortcut_stop = QShortcut(QKeySequence("F7"), self)
        self.shortcut_stop.activated.connect(self.on_shortcut_stop)
        
    def center_on_screen(self):
        """화면 중앙에 윈도우 배치"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def update_timer_label(self, time_str):
        """타이머 레이블 업데이트"""
        self.timer_label.setText(time_str)
        
    def on_start(self):
        """시작 버튼 클릭 이벤트"""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.main_ctrl.start_timer()
        self.statusBar().showMessage(self.lang_res.messages['TIMER_STARTED'])
        
    def on_pause(self):
        """일시정지 버튼 클릭 이벤트"""
        if self.pause_button.text() == self.lang_res.button_labels['PAUSE']:
            self.pause_button.setText(self.lang_res.button_labels['RESUME'])
            self.main_ctrl.pause_timer()
            self.statusBar().showMessage(self.lang_res.messages['TIMER_PAUSED'])
        else:
            self.pause_button.setText(self.lang_res.button_labels['PAUSE'])
            self.main_ctrl.resume_timer()
            self.statusBar().showMessage(self.lang_res.messages['TIMER_RESUMED'])
            
    def on_stop(self):
        """중지 버튼 클릭 이벤트"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText(self.lang_res.button_labels['PAUSE'])
        self.stop_button.setEnabled(False)
        self.main_ctrl.stop_timer()
        self.statusBar().showMessage(self.lang_res.messages['TIMER_STOPPED'])
        
    def on_settings(self):
        """설정 메뉴 클릭 이벤트"""
        settings_dialog = SettingsDialog(self, self.config_ctrl)
        if settings_dialog.exec_():
            # 설정이 변경되었으면 언어 리소스 다시 로드
            self.lang_res = load_language_resource(self.config_ctrl.get_language())
            # UI 텍스트 업데이트
            self.update_ui_texts()
            
    def on_about(self):
        """정보 메뉴 클릭 이벤트"""
        QMessageBox.about(
            self, 
            "PaceKeeper",
            self.lang_res.messages['ABOUT_TEXT']
        )
        
    def on_category(self):
        """카테고리 메뉴 클릭 이벤트"""
        category_dialog = CategoryDialog(self, self.config_ctrl)
        category_dialog.exec_()
        
    def on_logs(self):
        """로그 메뉴 클릭 이벤트"""
        log_dialog = LogDialog(self, self.config_ctrl)
        log_dialog.exec_()
        
    def on_tag_selected(self, tag):
        """태그 선택 이벤트"""
        self.main_ctrl.set_current_tag(tag)
        
    def on_text_changed(self, text):
        """텍스트 변경 이벤트"""
        self.main_ctrl.set_current_description(text)
        
    def on_log_double_clicked(self, index):
        """로그 항목 더블 클릭 이벤트"""
        # 로그 항목 더블 클릭 시 처리할 내용을 여기에 구현
        pass
        
    def update_ui_texts(self):
        """UI 텍스트 업데이트"""
        # 버튼 텍스트
        self.start_button.setText(self.lang_res.button_labels['START'])
        self.start_button.setToolTip(f"{self.lang_res.button_labels['START']} (F5)")
        
        if self.pause_button.isEnabled():
            if self.main_ctrl.timer_service.is_paused:
                self.pause_button.setText(self.lang_res.button_labels['RESUME'])
                self.pause_button.setToolTip(f"{self.lang_res.button_labels['RESUME']} (F6)")
            else:
                self.pause_button.setText(self.lang_res.button_labels['PAUSE'])
                self.pause_button.setToolTip(f"{self.lang_res.button_labels['PAUSE']} (F6)")
        
        self.stop_button.setText(self.lang_res.button_labels['STOP'])
        self.stop_button.setToolTip(f"{self.lang_res.button_labels['STOP']} (F7)")
        
        # 텍스트 입력 패널 힌트
        self.text_input_panel.set_hint(self.lang_res.messages['TASK_DESCRIPTION'])
        
        # 메뉴 텍스트
        self.menuBar().clear()
        self.init_menu()
        
        # 상태바 메시지
        if self.main_ctrl.timer_service.is_running:
            if self.main_ctrl.timer_service.is_paused:
                self.statusBar().showMessage(self.lang_res.messages['TIMER_PAUSED'])
            else:
                self.statusBar().showMessage(self.lang_res.messages['TIMER_STARTED'])
        else:
            self.statusBar().showMessage(self.lang_res.messages['READY'])
            
    def show_break_dialog(self, break_type, duration, on_break_end):
        """휴식 다이얼로그 표시"""
        break_dialog = BreakDialog(
            self, 
            self.main_ctrl, 
            self.config_ctrl,
            duration,
            on_break_end
        )
        break_dialog.show()
        
    def closeEvent(self, event):
        """윈도우 닫기 이벤트"""
        reply = QMessageBox.question(
            self, 
            "PaceKeeper",
            self.lang_res.messages['CONFIRM_EXIT'],
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 타이머 중지
            if self.main_ctrl.timer_service.is_running:
                self.main_ctrl.stop_timer()
            event.accept()
        else:
            event.ignore()
        
    def on_shortcut_start(self):
        """시작 단축키 이벤트"""
        if self.start_button.isEnabled():
            self.on_start()
            
    def on_shortcut_pause(self):
        """일시정지/재개 단축키 이벤트"""
        if self.pause_button.isEnabled():
            self.on_pause()
            
    def on_shortcut_stop(self):
        """중지 단축키 이벤트"""
        if self.stop_button.isEnabled():
            self.on_stop() 