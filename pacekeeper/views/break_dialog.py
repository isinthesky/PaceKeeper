from icecream import ic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import SET_BREAK_COLOR, SET_PADDING_SIZE
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.controllers.main_controller import MainController
from pacekeeper.utils.theme_manager import theme_manager
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

        # config에서 휴식 색상 가져오기 및 테마 속성 설정
        break_color = self.config.get_setting(SET_BREAK_COLOR, "#FDFFB6")
        # ThemeManager를 사용하여 휴식 다이얼로그 스타일 적용
        theme_manager.apply_break_dialog_style(self, break_color)

        # 타이머 정지를 위한 함수 지정
        self.stop_timer_func = self.main_controller.timer_service.stop

        self.init_ui()
        self.init_events()
        self.center_on_screen()

    def init_ui(self):
        """UI 구성: 안내 문구와 남은 시간 표시(타이머 라벨), 그리고 휴식 관련 버튼들 추가"""
        main_layout = QVBoxLayout(self)

        # 안내 문구
        info_label = QLabel(lang_res.messages['START_BREAK'], self)
        info_label.setAlignment(Qt.AlignCenter)
        theme_manager.apply_label_style(info_label, "break")
        main_layout.addWidget(info_label, 0, Qt.AlignCenter)
        main_layout.addSpacing(20)  # 간격 추가

        # 남은 시간 표시를 위한 타이머 라벨
        self.break_label = TimerLabel(self, "00:00", font_increment=10)
        self.break_label.setAlignment(Qt.AlignCenter)
        theme_manager.apply_label_style(self.break_label, "breakTimer")
        main_layout.addWidget(self.break_label, 0, Qt.AlignCenter)
        main_layout.addSpacing(30)  # 간격 추가

        # 버튼 컨테이너
        button_container = QVBoxLayout()

        # 작업 마무리 버튼들 (1분 뒤, 3분 뒤)
        finish_layout = QHBoxLayout()

        self.finish_1min_button = QPushButton("1분 뒤", self)
        theme_manager.apply_button_style(self.finish_1min_button, "secondary")
        theme_manager.set_widget_property(self.finish_1min_button, "break-finish", True)
        finish_layout.addWidget(self.finish_1min_button)

        self.finish_3min_button = QPushButton("3분 뒤", self)
        theme_manager.apply_button_style(self.finish_3min_button, "secondary")
        theme_manager.set_widget_property(self.finish_3min_button, "break-finish", True)
        finish_layout.addWidget(self.finish_3min_button)

        button_container.addLayout(finish_layout)
        button_container.addSpacing(15)

        # 휴식 닫기 버튼 (즉시 휴식)
        self.close_button = QPushButton("휴식 닫기", self)
        theme_manager.apply_button_style(self.close_button, "warning")
        theme_manager.set_widget_property(self.close_button, "break-close", True)
        button_container.addWidget(self.close_button, 0, Qt.AlignCenter)

        main_layout.addLayout(button_container)
        main_layout.addSpacing(20)  # 간격 추가

    def init_events(self):
        """이벤트 바인딩: 다이얼로그 종료 시 타이머 정지 처리 및 모든 버튼 이벤트 바인딩"""
        self.close_button.clicked.connect(self.on_close_button)
        self.finish_1min_button.clicked.connect(lambda: self.on_finish_later(1))
        self.finish_3min_button.clicked.connect(lambda: self.on_finish_later(3))

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
        try:
            ic("휴식 닫기 버튼 클릭")
            if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
                self.stop_timer_func()
            self.on_break_finish()
            self.accept()
        except Exception as e:
            ic(f"휴식 닫기 처리 중 오류: {e}")
            # 오류 발생 시에도 다이얼로그는 닫기
            try:
                self.accept()
            except Exception as inner_e:
                ic(f"다이얼로그 닫기 중 추가 오류: {inner_e}")

    def on_finish_later(self, minutes):
        """
        작업 마무리 버튼 (1분 뒤, 3분 뒤) 클릭 시 호출되는 이벤트 핸들러
        현재 휴식 타이머를 중지하고 지정된 시간 후 휴식을 시작하도록 설정합니다.
        """
        try:
            ic(f"{minutes}분 뒤 휴식 시작 요청")

            # 현재 휴식 타이머 중지
            if hasattr(self, 'stop_timer_func') and callable(self.stop_timer_func):
                self.stop_timer_func()

            # 작업 마무리 타이머 시작 (지정된 분 후에 다시 휴식 다이얼로그 표시)
            total_seconds = minutes * 60

            # 새로운 타이머 콜백 설정: 작업 마무리 후 다시 휴식 시작
            def on_finish_work_complete():
                ic("작업 마무리 완료, 휴식 다이얼로그 다시 표시")

                # mini mode에서 일반 모드로 복원 (휴식 다이얼로그 표시 전)
                if hasattr(self.main_controller, 'main_window') and self.main_controller.main_window:
                    self.main_controller.main_window.restore_main_controls()
                    theme_manager.set_widget_property(self.main_controller.main_window, "miniMode", False)
                    ic("mini mode에서 일반 모드로 복원 완료")

                # 휴식 세션 다시 시작
                self.main_controller.start_break_session(self.break_minutes)

            # 타이머 서비스에 새로운 콜백과 함께 타이머 시작
            self.main_controller.timer_service.on_finish = on_finish_work_complete
            self.main_controller.timer_service.start(total_seconds)

            # 메인 윈도우를 mini mode로 설정 (작업 마무리 시간 동안)
            if hasattr(self.main_controller, 'main_window') and self.main_controller.main_window:
                # 메인 윈도우를 mini mode로 설정
                self.main_controller.main_window.hide_main_controls()
                theme_manager.set_widget_property(self.main_controller.main_window, "miniMode", True)

                # 타이머 라벨에 작업 마무리 상태 표시
                self.main_controller.main_window.timer_label.setText(f"{minutes:02d}:00")

                # 버튼 상태를 작업 마무리 모드로 설정
                self.main_controller.main_window.start_button.setText(f"{minutes}분 후 휴식")
                self.main_controller.main_window.start_button.setEnabled(True)  # 중단할 수 있도록 활성화
                self.main_controller.main_window.pause_button.setEnabled(True)  # 일시정지 가능
                self.main_controller.main_window.pause_button.setText(lang_res.button_labels.get('PAUSE', "PAUSE"))

                # 타이머 업데이트 콜백 설정
                self.main_controller.timer_service.update_callback = self.main_controller.main_window.update_timer_label

            # 다이얼로그 종료 (휴식 종료 콜백은 호출하지 않음)
            self._destroyed = True  # 중복 호출 방지
            self.accept()

            ic(f"{minutes}분 후 휴식 설정 완료")

        except Exception as e:
            ic(f"작업 마무리 처리 중 오류 발생: {e}")
            # 오류 발생 시 일반 휴식 닫기 처리
            self.on_close_button()

    def on_break_finish(self):
        """
        타이머 종료 및 휴식 중 강제 종료 시 호출되는 메서드
        on_break_end 콜백을 호출합니다.
        """
        if not self._destroyed and self.on_break_end:
            self._destroyed = True  # 중복 호출 방지
            self.on_break_end()
            self.on_break_end = None  # 콜백 참조 제거
