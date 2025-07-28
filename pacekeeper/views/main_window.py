# views/main_window.py
import re  # 추가: 해시태그 검사를 위한 정규식 모듈
from typing import Any

from icecream import ic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QAction,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pacekeeper.consts.labels import load_language_resource
from pacekeeper.consts.settings import APP_TITLE, SET_MAIN_DLG_HEIGHT, SET_MAIN_DLG_WIDTH
from pacekeeper.controllers.config_controller import ConfigController
from pacekeeper.services.app_state_manager import AppStatus
from pacekeeper.utils.theme_manager import theme_manager
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.views.category_dialog import CategoryDialog
from pacekeeper.views.controls import RecentLogsControl, TagButtonsPanel, TextInputPanel, TimerLabel
from pacekeeper.views.log_dialog import LogDialog
from pacekeeper.views.settings_dialog import SettingsDialog

lang_res = load_language_resource(ConfigController().get_language())

class MainWindow(QMainWindow):
    """
    MainWindow: UI View 컴포넌트
    책임: UI 구성, 레이아웃 초기화, 이벤트 바인딩 및 MainController와의 상호작용
    """
    def __init__(self, main_controller: Any | None = None, config_ctrl: Any | None = None) -> None:
        if config_ctrl is None:
            config_ctrl = ConfigController()

        width = config_ctrl.get_setting(SET_MAIN_DLG_WIDTH, 800)
        height = config_ctrl.get_setting(SET_MAIN_DLG_HEIGHT, 550)
        super().__init__(None)
        self.setWindowTitle(APP_TITLE)
        self.resize(width, height)
        self.config_ctrl = config_ctrl
        self.main_controller = main_controller

        # 중앙 위젯 설정
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # UI 구성 및 이벤트 바인딩
        self.init_ui()
        self.init_menu()
        self.init_events()
        self.apply_theme()

        self.original_size = self.size()
        self.study_size = QSize(220, 160)  # 더 자연스러운 직사각형 비율 (2:1)

    def hide_main_controls(self) -> None:
        """
        학습 타이머 실행 시, recent_logs(리스트 컨트롤), tag_panel(태그 버튼),
        log_input_panel(텍스트 입력 컨트롤)을 숨기고 창 크기를 작게 만듭니다.
        """
        try:
            ic("UI 컨트롤 숨기기 시작")

            # 컨트롤 숨기기
            if hasattr(self, "recent_logs") and self.recent_logs is not None:
                self.recent_logs.hide()
                ic("recent_logs 숨김")

            if hasattr(self, "tag_panel") and self.tag_panel is not None:
                self.tag_panel.hide()
                ic("tag_panel 숨김")

            if hasattr(self, "log_input_panel") and self.log_input_panel is not None:
                self.log_input_panel.hide()
                ic("log_input_panel 숨김")

            # 창 크기 변경 및 제약 제거
            self.setMinimumSize(0, 0)  # 최소 크기 제약 제거
            self.setMaximumSize(16777215, 16777215)  # 최대 크기 제약 제거
            self.resize(self.study_size)
            self.setFixedSize(self.study_size)  # 고정 크기로 설정
            ic(f"창 크기를 {self.study_size.width()}x{self.study_size.height()}로 변경")
        except Exception as e:
            ic(f"UI 컨트롤 숨기기 중 오류 발생: {e}")

    def restore_main_controls(self) -> None:
        """
        쉬는 시간 종료 후, 숨겨진 컨트롤들을 다시 보이고 원래 창 크기로 복원합니다.
        """
        try:
            ic("UI 컨트롤 복원 시작")

            # 컨트롤 표시
            if hasattr(self, "recent_logs") and self.recent_logs is not None:
                self.recent_logs.show()
                ic("recent_logs 표시")

            if hasattr(self, "tag_panel") and self.tag_panel is not None:
                self.tag_panel.show()
                ic("tag_panel 표시")

            if hasattr(self, "log_input_panel") and self.log_input_panel is not None:
                self.log_input_panel.show()
                ic("log_input_panel 표시")

            # 창 크기 복원 및 제약 제거
            self.setMinimumSize(0, 0)  # 최소 크기 제약 제거
            self.setMaximumSize(16777215, 16777215)  # 최대 크기 제약 제거
            self.resize(self.original_size)
            ic(f"창 크기를 {self.original_size.width()}x{self.original_size.height()}로 복원")
        except Exception as e:
            ic(f"UI 컨트롤 복원 중 오류 발생: {e}")

    def init_ui(self) -> None:
        """UI 컴포넌트 초기화 및 레이아웃 구성"""
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(6)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        # 타이머 라벨 (카드 없이 직접 배치)
        self.timer_label = TimerLabel(self.central_widget, initial_text="00:00", font_increment=20, bold=True)
        theme_manager.apply_label_style(self.timer_label, "timer")
        self.main_layout.addWidget(self.timer_label, 0, Qt.AlignCenter)
        self.main_layout.addSpacing(8)

        # 최근 기록 표시 영역 (단순화)
        self.recent_logs = RecentLogsControl(
            self.central_widget, self.config_ctrl,
            on_double_click=self.on_log_double_click,
            on_logs_updated=self.update_tag_buttons
        )
        ic("RecentLogsControl 초기화 완료, on_logs_updated 콜백 설정됨")
        self.main_layout.addWidget(self.recent_logs, 1)

        # 태그 버튼 패널 (단순화)
        self.tag_panel = TagButtonsPanel(self.central_widget, on_tag_selected=self.add_tag_to_input)
        self.main_layout.addWidget(self.tag_panel)
        # RecentLogsControl의 update_logs 호출 시 update_tag_buttons()가 자동 호출됩니다.

        # 텍스트 입력 패널 (단순화)
        self.log_input_panel = TextInputPanel(self.central_widget, on_text_changed=self.on_log_input_text_change)
        self.main_layout.addWidget(self.log_input_panel)

        # 시작/중지 버튼 패널 (단순화)
        self.button_panel = QWidget(self.central_widget)
        button_layout = QHBoxLayout(self.button_panel)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 시작 버튼 (토글 버튼으로 Start/Stop 기능 수행)
        self.start_button = QPushButton(lang_res.button_labels.get('START', "START"), self.button_panel)
        theme_manager.apply_button_style(self.start_button, "primary")
        # 일시정지 버튼
        self.pause_button = QPushButton(lang_res.button_labels.get('PAUSE', "PAUSE"), self.button_panel)
        theme_manager.apply_button_style(self.pause_button, "secondary")

        self.pause_button.setEnabled(False)

        button_layout.addWidget(self.start_button, 1)
        button_layout.addWidget(self.pause_button, 1)
        self.main_layout.addWidget(self.button_panel)

        self.update_tag_buttons()
        self.update_start_button_state()

    def init_menu(self) -> None:
        """메뉴바 초기화 및 메뉴 아이템 생성"""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu(lang_res.base_labels['FILE'])

        # 설정 메뉴 아이템
        self.settings_action = QAction(lang_res.base_labels['SETTINGS'], self)
        self.settings_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.settings_action)

        # 로그 메뉴 아이템
        self.track_action = QAction(lang_res.base_labels['LOGS'], self)
        self.track_action.setShortcut("Ctrl+L")
        file_menu.addAction(self.track_action)

        # 카테고리 메뉴 아이템
        self.category_action = QAction(lang_res.base_labels['CATEGORY'], self)
        self.category_action.setShortcut("Ctrl+C")
        file_menu.addAction(self.category_action)

        # 종료 메뉴 아이템
        self.exit_action = QAction(lang_res.base_labels['EXIT'], self)
        self.exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(self.exit_action)

    def init_events(self) -> None:
        """이벤트 바인딩"""
        # 메뉴 이벤트 연결
        self.settings_action.triggered.connect(self.on_open_settings)
        self.track_action.triggered.connect(self.on_show_track)
        self.category_action.triggered.connect(self.on_show_category)
        self.exit_action.triggered.connect(self.on_exit)

        # 버튼 이벤트 연결
        self.start_button.clicked.connect(self.on_toggle_timer)
        self.pause_button.clicked.connect(self.on_pause)

    def update_tag_buttons(self) -> None:
        """
        최근 로그에서 태그를 추출하여 TagButtonsPanel을 업데이트합니다.
        """
        # tag_panel이 아직 설정되지 않았으면 아무런 작업도 수행하지 않습니다.
        if not hasattr(self, "tag_panel"):
            ic("tag_panel이 아직 초기화되지 않았습니다.")
            return

        ic("update_tag_buttons 메서드 호출됨")

        try:
            # MainController를 통해 태그 서비스에 접근
            if not self.main_controller:
                ic("MainController가 없어서 태그를 가져올 수 없습니다.")
                return

            # 태그 가져오기 시도
            tags = self.main_controller.tag_service.get_tags()

            # 태그가 None이면 빈 리스트로 처리
            if tags is None:
                ic("태그 서비스에서 None을 반환했습니다. 빈 리스트로 처리합니다.")
                tags = []

            ic(f"태그 서비스에서 {len(tags)} 개의 태그를 가져왔습니다.")

            # 태그 패널이 유효한지 확인
            if not hasattr(self, "tag_panel") or self.tag_panel is None:
                ic("태그 패널이 유효하지 않습니다.")
                return

            # 태그 패널 업데이트
            self.tag_panel.update_tags(tags)
            ic("태그 버튼 업데이트 완료")
        except Exception as e:
            ic(f"태그 업데이트 중 오류 발생: {e}")
            # 오류 발생 시 빈 태그 리스트로 업데이트 시도
            try:
                if hasattr(self, "tag_panel") and self.tag_panel is not None:
                    self.tag_panel.update_tags([])
            except Exception as inner_e:
                ic(f"빈 태그 리스트로 업데이트 시도 중 오류 발생: {inner_e}")

    def on_log_double_click(self, row: int) -> None:
        """최근 로그 리스트의 항목을 더블 클릭했을 때, 해당 로그 메시지를 log_input_panel에 복사"""
        try:
            ic(f"로그 더블 클릭 이벤트 발생, 행: {row}")

            # 로그 메시지 가져오기
            message = self.recent_logs.get_message_at(row)

            # 메시지가 비어있는지 확인
            if not message:
                ic("가져온 메시지가 비어 있습니다.")
                return

            # 입력 필드에 메시지 설정
            self.log_input_panel.set_value(message)
            ic(f"입력 필드에 메시지 '{message}' 설정됨")
        except Exception as e:
            ic(f"로그 더블 클릭 처리 중 오류 발생: {e}")

    def on_open_settings(self) -> None:
        """설정 다이얼로그 오픈"""
        dlg = SettingsDialog(self, self.config_ctrl)
        dlg.exec_()

    def on_show_track(self) -> None:
        """로그 다이얼로그 오픈"""
        # MainController의 서비스들을 LogDialog에 전달
        if self.main_controller:
            dlg = LogDialog(
                self,
                self.config_ctrl,
                self.main_controller.log_service,
                self.main_controller.tag_service
            )
            dlg.exec_()
        else:
            ic("MainController가 없어서 로그 다이얼로그를 열 수 없습니다.")

    def on_show_category(self) -> None:
        """카테고리 다이얼로그 오픈"""
        # MainController의 서비스들을 CategoryDialog에 전달
        if self.main_controller:
            dlg = CategoryDialog(
                self,
                self.config_ctrl,
                self.main_controller.category_service,
                self.main_controller.tag_service
            )
            dlg.exec_()
        else:
            ic("MainController가 없어서 카테고리 다이얼로그를 열 수 없습니다.")

    def on_exit(self) -> None:
        """앱 종료 처리"""
        self.close()

    def on_toggle_timer(self) -> None:
        """
        타이머 시작/중단 토글 이벤트 핸들러
        study timer 시작 시 주요 컨트롤(최근 로그, 태그 버튼, 텍스트 입력)을 숨기고 창 크기를 축소합니다.
        """
        try:
            # 현재 버튼이 "X분 후 휴식" 상태인지 확인
            button_text = self.start_button.text()
            if "분 후 휴식" in button_text:
                # 작업 마무리 타이머 중지 및 즉시 휴식으로 전환
                ic("작업 마무리 타이머 중지 요청")
                self.main_controller.timer_service.stop()
                self.toggle_buttons(AppStatus.WAIT)
                return

            if not self.main_controller.timer_service.is_running():
                # 타이머가 실행 중이 아니면 학습 세션 시작
                ic("타이머 시작 요청")

                # 입력 필드에 해시태그가 있는지 확인
                text = self.log_input_panel.get_value() or ""
                if not re.search(r'#\w+', text):
                    ic("입력 필드에 해시태그가 없습니다. 타이머를 시작할 수 없습니다.")
                    return

                # UI 업데이트
                self.start_button.setText(lang_res.button_labels.get('STOP', "STOP"))
                self.pause_button.setEnabled(True)

                # 타이머 시작
                ic("학습 세션 시작")
                self.main_controller.start_study_session()

                # 컨트롤 숨기기 및 작은 창으로 전환 (미니 모드 활성화)
                ic("UI 컨트롤 숨기기 및 창 크기 축소")
                self.hide_main_controls()
                # 미니 모드 속성 설정
                theme_manager.set_widget_property(self, "miniMode", True)
            else:
                # 타이머가 실행 중이면 강제 종료 처리 및 UI 복원
                ic("타이머 중지 요청")

                # 타이머 중지
                self.main_controller.stop_study_timer()

                # UI 업데이트
                self.start_button.setText(lang_res.button_labels.get('START', "START"))
                self.pause_button.setEnabled(False)
                self.timer_label.setText("00:00")

                # 원래 UI 복원 (미니 모드 비활성화)
                ic("UI 컨트롤 복원 및 창 크기 원복")
                self.restore_main_controls()
                # 미니 모드 속성 제거
                theme_manager.set_widget_property(self, "miniMode", False)

            # 시작 버튼 상태 업데이트
            self.update_start_button_state()
        except Exception as e:
            ic(f"타이머 토글 중 오류 발생: {e}")
            # 오류 발생 시 UI 복원 시도
            try:
                self.start_button.setText(lang_res.button_labels.get('START', "START"))
                self.pause_button.setEnabled(False)
                self.timer_label.setText("00:00")
                self.restore_main_controls()
            except Exception as inner_e:
                ic(f"오류 복구 중 추가 오류 발생: {inner_e}")

    def on_pause(self) -> None:
        """
        타이머 일시정지/재개 이벤트 핸들러
        수정: MainController의 토글 메서드를 활용하고, timer_service의 상태로 버튼 라벨 변경
        """
        try:
            ic("타이머 일시정지/재개 요청")

            # 타이머 서비스가 초기화되었는지 확인
            if not hasattr(self, "main_controller") or not hasattr(self.main_controller, "timer_service"):
                ic("타이머 서비스가 초기화되지 않았습니다.")
                return

            # 타이머 일시정지/재개 토글
            self.main_controller.toggle_pause()

            # 버튼 라벨 업데이트
            if self.main_controller.timer_service.is_paused():
                ic("타이머가 일시정지되었습니다.")
                self.pause_button.setText(lang_res.button_labels.get('RESUME', "RESUME"))
            else:
                ic("타이머가 재개되었습니다.")
                self.pause_button.setText(lang_res.button_labels.get('PAUSE', "PAUSE"))
        except Exception as e:
            ic(f"타이머 일시정지/재개 중 오류 발생: {e}")

    def add_tag_to_input(self, tag):
        """
        태그를 입력 필드에 추가합니다.
        """
        try:
            # 태그 유효성 검사
            if not isinstance(tag, dict) or 'name' not in tag:
                ic(f"유효하지 않은 태그 형식: {tag}")
                return

            # 현재 입력 필드 값 가져오기
            current = self.log_input_panel.get_value()
            tag_name = tag['name']

            # 태그가 이미 입력 필드에 있는지 확인
            tag_pattern = f"#{tag_name}"
            if tag_pattern in current:
                ic(f"태그 '{tag_name}'이(가) 이미 입력 필드에 있습니다.")
                return

            # 태그 추가
            new_text = f"{current} #{tag_name}" if current else f"#{tag_name}"
            self.log_input_panel.set_value(new_text.strip())
            ic(f"태그 '{tag_name}'이(가) 입력 필드에 추가되었습니다.")

            # 시작 버튼 상태 업데이트
            self.update_start_button_state()
        except Exception as e:
            ic(f"태그 추가 중 오류 발생: {e}")

    def update_timer_label(self, time_str: str):
        """타이머 라벨 업데이트 (Controller에서 호출)

           메인 타이머 라벨(self.timer_label)과, 휴식 다이얼로그가 열려 있다면 그 안의
           타이머 라벨(self.break_label) 모두 업데이트합니다.
        """
        try:
            # 타이머 라벨 유효성 검사
            if not hasattr(self, "timer_label") or self.timer_label is None:
                ic("타이머 라벨이 유효하지 않습니다.")
                return

            # 메인 타이머 라벨 업데이트
            self.timer_label.setText(time_str)

            # 휴식 다이얼로그 타이머 라벨 업데이트
            if hasattr(self, "break_dialog") and self.break_dialog is not None:
                if hasattr(self.break_dialog, "break_label"):
                    self.break_dialog.break_label.setText(time_str)
                    ic(f"휴식 다이얼로그 타이머 라벨 업데이트: {time_str}")
        except Exception as e:
            ic(f"타이머 라벨 업데이트 중 오류 발생: {e}")

    def show_break_dialog(self, break_min):
        """
        휴식 다이얼로그를 표시합니다.
        """
        try:
            ic(f"휴식 다이얼로그 표시 요청, 휴식 시간: {break_min}분")

            # 휴식 종료 콜백 함수 정의
            def on_break_end():
                try:
                    ic("휴식 종료 콜백 실행")
                    # 쉬는 시간 종료 후 UI 초기화
                    self.start_button.setText(lang_res.button_labels.get('START', "START"))
                    self.pause_button.setEnabled(False)
                    self.log_input_panel.set_value("")
                    self.update_start_button_state()
                    self.restore_main_controls()  # 숨긴 컨트롤 복원 및 원래 창 크기로 복구
                    ic("휴식 종료 후 UI 초기화 완료")
                except Exception as e:
                    ic(f"휴식 종료 콜백 실행 중 오류 발생: {e}")

            # 휴식 다이얼로그 생성
            ic("휴식 다이얼로그 생성")
            self.break_dialog = BreakDialog(
                self,
                self.main_controller,
                self.config_ctrl,
                break_minutes=break_min,
                on_break_end=on_break_end
            )

            # 타이머 업데이트 콜백 저장 및 변경
            original_update_callback = self.main_controller.timer_service.update_callback

            def break_update(time_str):
                try:
                    if self.break_dialog and hasattr(self.break_dialog, "break_label"):
                        self.break_dialog.break_label.setText(time_str)
                        # ic(f"휴식 타이머 업데이트: {time_str}")  # 너무 많은 로그 방지
                except Exception as e:
                    ic(f"휴식 타이머 업데이트 중 오류 발생: {e}")

            ic("타이머 업데이트 콜백 변경")
            self.main_controller.timer_service.update_callback = break_update

            # 다이얼로그 표시
            ic("휴식 다이얼로그 표시")
            self.break_dialog.exec_()

            # 타이머 업데이트 콜백 복원
            ic("타이머 업데이트 콜백 복원")
            self.main_controller.timer_service.update_callback = original_update_callback

            # 다이얼로그 정리
            self.break_dialog = None
            ic("휴식 다이얼로그 정리 완료")
        except Exception as e:
            ic(f"휴식 다이얼로그 표시 중 오류 발생: {e}")
            # 오류 발생 시 타이머 업데이트 콜백 복원 시도
            try:
                if hasattr(self, "main_controller") and hasattr(self.main_controller, "timer_service"):
                    self.main_controller.timer_service.update_callback = original_update_callback
            except Exception as inner_e:
                ic(f"오류 복구 중 추가 오류 발생: {inner_e}")

    def closeEvent(self, event):
        """창 닫기 시 타이머 스레드 정리"""
        try:
            ic("애플리케이션 종료 요청")

            # 타이머 서비스 정리
            if hasattr(self, "main_controller") and hasattr(self.main_controller, "timer_service"):
                ic("타이머 서비스 정리")
                self.main_controller.timer_service.stop()

            # 이벤트 수락
            event.accept()
            ic("애플리케이션 종료 처리 완료")
        except Exception as e:
            ic(f"애플리케이션 종료 처리 중 오류 발생: {e}")
            # 오류가 발생해도 종료는 진행
            event.accept()

    def set_main_controller(self, main_controller) -> None:
        """MainController 설정 (의존성 주입 후 호출)"""
        self.main_controller = main_controller

        # TagButtonsPanel에 category_service 설정
        if hasattr(self, 'tag_panel') and self.tag_panel:
            self.tag_panel.category_service = main_controller.category_service

    # 텍스트 입력 변경 이벤트 핸들러
    def on_log_input_text_change(self, text=None):
        """
        텍스트 입력 필드의 내용이 변경될 때 호출되는 이벤트 핸들러
        
        Args:
            text: 변경된 텍스트 (optional)
        """
        try:
            # 입력 텍스트 로깅 (너무 많은 로그 방지)
            # if text:
            #     ic(f"텍스트 입력 변경: '{text}'")

            # 시작 버튼 상태 업데이트
            self.update_start_button_state()
        except Exception as e:
            ic(f"텍스트 입력 변경 처리 중 오류 발생: {e}")
            # 오류 발생 시 안전한 기본 상태로 복원
            try:
                self.start_button.setEnabled(False)
            except Exception as inner_e:
                ic(f"기본 상태 복원 중 추가 오류: {inner_e}")

    def update_start_button_state(self):
        """
        입력 필드의 내용에 따라 시작 버튼의 활성화 상태를 업데이트합니다.
        """
        try:
            # 세션 중이면 start_button은 항상 활성화 (STOP용)
            if hasattr(self, "main_controller") and self.main_controller.timer_service.is_running():
                ic("타이머가 실행 중입니다. 시작 버튼을 활성화합니다.")
                self.start_button.setEnabled(True)
                return

            # 입력 필드 값 가져오기
            text = self.log_input_panel.get_value() or ""

            # 해시태그 패턴: '#' 뒤에 하나 이상의 알파벳, 숫자, 언더스코어가 오는 경우
            has_hashtag = bool(re.search(r'#\w+', text))

            # 버튼 상태 업데이트
            if has_hashtag:
                ic(f"입력 필드에 해시태그가 있습니다: '{text}'. 시작 버튼을 활성화합니다.")
                self.start_button.setEnabled(True)
            else:
                ic(f"입력 필드에 해시태그가 없습니다: '{text}'. 시작 버튼을 비활성화합니다.")
                self.start_button.setEnabled(False)
        except Exception as e:
            ic(f"시작 버튼 상태 업데이트 중 오류 발생: {e}")
            # 오류 발생 시 기본적으로 버튼 비활성화
            self.start_button.setEnabled(False)

    def toggle_buttons(self, status: AppStatus) -> None:
        """
        앱 상태에 따라 버튼들의 상태를 업데이트합니다.
        
        Args:
            status: 새로운 앱 상태
        """
        try:
            ic(f"버튼 상태 업데이트: {status}")

            if status == AppStatus.WAIT:
                # 대기 상태: 시작 버튼 활성화, 일시정지 버튼 비활성화
                self.start_button.setText(lang_res.button_labels.get('START', "START"))
                self.start_button.setEnabled(True)  # 해시태그 확인은 update_start_button_state에서
                self.pause_button.setEnabled(False)
                self.pause_button.setText(lang_res.button_labels.get('PAUSE', "PAUSE"))
                self.timer_label.setText("00:00")

                # 미니 모드에서 일반 모드로 복원
                self.restore_main_controls()
                theme_manager.set_widget_property(self, "miniMode", False)

            elif status == AppStatus.STUDY:
                # 학습 상태: 중지 버튼으로 변경, 일시정지 버튼 활성화
                self.start_button.setText(lang_res.button_labels.get('STOP', "STOP"))
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(True)
                self.pause_button.setText(lang_res.button_labels.get('PAUSE', "PAUSE"))

                # 미니 모드 활성화
                self.hide_main_controls()
                theme_manager.set_widget_property(self, "miniMode", True)

            elif status == AppStatus.PAUSED:
                # 일시정지 상태: 재개 버튼으로 변경
                self.pause_button.setText(lang_res.button_labels.get('RESUME', "RESUME"))

            elif status in [AppStatus.SHORT_BREAK, AppStatus.LONG_BREAK]:
                # 휴식 상태: 버튼들 비활성화
                self.start_button.setEnabled(False)
                self.pause_button.setEnabled(False)

            # 해시태그 체크 기반 시작 버튼 상태 업데이트
            if status == AppStatus.WAIT:
                self.update_start_button_state()

            ic(f"버튼 상태 업데이트 완료: {status}")

        except Exception as e:
            ic(f"버튼 상태 업데이트 중 오류 발생: {e}")

    def apply_theme(self) -> None:
        """현대적인 테마 적용"""
        try:
            # 전체 애플리케이션에 테마 적용
            theme_manager.apply_theme()
            ic("현대적인 테마 적용 완료")
        except Exception as e:
            ic(f"테마 적용 중 오류 발생: {e}")
