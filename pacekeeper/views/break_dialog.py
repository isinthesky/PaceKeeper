from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QScreen, QGuiApplication

from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_PADDING_SIZE, SET_BREAK_COLOR
from pacekeeper.views.controls import TimerLabel

lang_res = load_language_resource(ConfigController().get_language())

class BreakDialog(QDialog):
    """
    휴식 시간을 카운트다운하는 모달 다이얼로그 및 UI 패널 통합 클래스
    
    주요 기능:
      - 안내 문구와 남은 시간 표시(타이머 라벨) 제공
      - 타이머 중지 및 다이얼로그 종료 이벤트 처리
      - 타이머 종료 시 on_break_end 콜백 실행
      - '휴식 닫기' 버튼을 통한 휴식 종료 기능 추가
    """
    def __init__(self, parent, main_controller: MainController, config_ctrl: ConfigController, break_minutes=5, on_break_end=None):
        super().__init__(parent)
        
        self.main_controller = main_controller
        self.config = config_ctrl
        self.break_minutes = break_minutes
        self.on_break_end = on_break_end
        self._destroyed = False
        
        # 디스플레이 전체 크기를 고려하여 대화상자 크기 설정
        screen_size = QGuiApplication.primaryScreen().size()
        dlg_width = screen_size.width() - self.config.get_setting(SET_PADDING_SIZE, 100)
        dlg_height = screen_size.height() - self.config.get_setting(SET_PADDING_SIZE, 100)
        
        # 다이얼로그 제목 및 크기 설정
        self.setWindowTitle(lang_res.title_labels['BREAK_DIALOG_TITLE'])
        self.resize(dlg_width, dlg_height)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 추가: config에 저장된 SET_BREAK_COLOR 값으로 배경색 설정 (기본값 "#FDFFB6")
        bg_color = self.config.get_setting(SET_BREAK_COLOR, "#FDFFB6")
        self.setStyleSheet(f"background-color: {bg_color};")
        
        # 타이머 정지를 위한 함수 지정
        self.stop_timer_func = self.main_controller.timer_service.stop
        
        self.init_ui()
        self.init_events()
        self.center_on_screen()
        
    def init_ui(self):
        """UI 구성: 안내 문구와 남은 시간 표시(타이머 라벨), 그리고 휴식 닫기 버튼 추가"""
        main_layout = QVBoxLayout(self)
        
        # 안내 문구
        info_label = QLabel(lang_res.messages['START_BREAK'], self)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: black;")  # 라벨 폰트 색상을 검정색으로 지정
        main_layout.addWidget(info_label, 0, Qt.AlignCenter)
        main_layout.addSpacing(20)  # 간격 추가
        
        # 남은 시간 표시를 위한 타이머 라벨
        self.break_label = TimerLabel(self, "00:00", font_increment=10)
        self.break_label.setAlignment(Qt.AlignCenter)
        self.break_label.setStyleSheet("color: black;")  # 타이머 라벨의 폰트 색상을 검정색으로 지정
        main_layout.addWidget(self.break_label, 0, Qt.AlignCenter)
        main_layout.addSpacing(20)  # 간격 추가
        
        # 휴식 닫기 버튼 추가
        self.close_button = QPushButton("휴식 닫기", self)
        self.close_button.setStyleSheet("background-color: #797979;")
        main_layout.addWidget(self.close_button, 0, Qt.AlignCenter)
        main_layout.addSpacing(20)  # 간격 추가
        
    def init_events(self):
        """이벤트 바인딩: 다이얼로그 종료 시 타이머 정지 처리 및 휴식 닫기 버튼 이벤트 바인딩"""
        self.close_button.clicked.connect(self.on_close_button)
        
    def center_on_screen(self):
        """화면 중앙에 다이얼로그 배치"""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def closeEvent(self, event):
        """다이얼로그 종료 시 타이머 정지 및 리소스 정리"""
        if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
            self.stop_timer_func()
        self.on_break_finish()
        event.accept()
        
    def on_close_button(self):
        """
        휴식 닫기 버튼 클릭 시 호출되는 이벤트 핸들러
        타이머를 정지시키고 휴식 종료 처리 후 다이얼로그를 종료합니다.
        """
        if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
            self.stop_timer_func()
        self.on_break_finish()
        self.accept()
        
    def on_break_finish(self):
        """
        타이머 종료 및 휴식 중 강제 종료 시 호출되는 메서드  
        on_break_end 콜백을 호출합니다.
        """
        if not self._destroyed and self.on_break_end:
            self._destroyed = True  # 중복 호출 방지
            self.on_break_end()
            self.on_break_end = None  # 콜백 참조 제거