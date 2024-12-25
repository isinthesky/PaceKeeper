import time
import wx
import threading
from breaktrack.controllers.config_controller import ConfigController, AppStatus
from breaktrack.views.break_dialog import BreakDialog
from breaktrack.models.data_model import DataModel
from breaktrack.controllers.sound_manager import SoundManager
from breaktrack.controllers.timer_thread import TimerThread
from breaktrack.const import CONFIG_DATA_MODEL, DIALOG_BREAK
class MainController:
    """
    메인 프레임과 상호작용하며,
    (1) Pomodoro cycle(공부->휴식->공부...) 흐름 제어
    (2) UI 이벤트 바인딩
    (3) 타이머 쓰레드 관리
    """

    def __init__(self, main_frame, config_controller: ConfigController):
        self.main_frame = main_frame
        self.config = config_controller
        self.sound_manager = SoundManager()

        # 사운드 파일 정의
        self.long_break_sound = "assets/sounds/long_brk.wav"
        self.short_break_sound = "assets/sounds/short_brk.wav"

        # 이벤트 바인딩
        self.main_frame.start_button.Bind(wx.EVT_BUTTON, self.toggle_timer)
        self.main_frame.Bind(wx.EVT_CLOSE, self.on_close)

        # TimerThread 초기값
        self.timer_thread = None

    def toggle_timer(self, event):
        """
        '시작' 또는 '중지' 버튼을 누를 때 실행.
        """
        if not self.config.is_running:
            self.start_timer()
        else:
            self.stop_timer()

    def start_timer(self):
        """
        타이머 시작 (공부 시간 -> 휴식 -> 반복)
        """
        self.config.start_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, False)
        self.main_frame.start_button.SetLabel("중지")

        # Pomodoro 사이클 관리
        # 메인 쓰레드에서 진행하면 GUI가 멈출 수 있으므로 별도 쓰레드 사용
        self.cycle_thread = threading.Thread(target=self.run_pomodoro_cycle, daemon=True)
        self.cycle_thread.start()

    def stop_timer(self):
        """
        타이머 중지
        """
        self.config.stop_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, True)
        self.main_frame.start_button.SetLabel("시작")

        # 메인 타이머 쓰레드 중지
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.stop()
            self.timer_thread.join(timeout=2)

        # UI 라벨 초기화
        wx.CallAfter(self.main_frame.timer_label.SetLabel, "00:00")

    def run_pomodoro_cycle(self):
        """
        - (1) '공부 시간' 카운트다운
        - (2) 사이클 횟수에 따라 '짧은 휴식' 또는 '긴 휴식' 결정
        - (3) 휴식 다이얼로그 표시
        - (4) 사용자 종료 또는 모든 사이클 반복
        """
        while self.config.is_running:
            self.config.increment_cycle()  # 사이클 증가

            # (A) 공부 시간 카운트다운
            study_time_min = self.config.get_setting("study_time", 25)
            total_seconds = study_time_min * 60
            self.start_study_countdown(total_seconds)

            if not self.config.is_running:
                break

            # (B) 휴식 시간 결정 (짧은 or 긴)
            if self.config.get_cycle() % self.config.get_setting("cycles", 4) == 0:
                # 긴 휴식
                self.sound_manager.play_sound(self.long_break_sound)
                break_min = self.config.get_setting("long_break", 15)
                self.config.set_status(AppStatus.LONG_BREAK)
            else:
                # 짧은 휴식
                self.sound_manager.play_sound(self.short_break_sound)
                break_min = self.config.get_setting("short_break", 5)
                self.config.set_status(AppStatus.SHORT_BREAK)

            # (C) 휴식 다이얼로그(모달) 표시
            wx.CallAfter(self.show_break_dialog, break_min)

            # 휴식 다이얼로그가 닫힐 때까지 대기
            while self.config.is_running and AppStatus.is_break(self.config.get_status()):
                time.sleep(1)

    def start_study_countdown(self, total_seconds):
        """
        공부 시간 카운트다운을 별도 TimerThread로 처리
        """
        self.timer_thread = TimerThread(
            config_controller=self.config,
            main_frame=self.main_frame,
            total_seconds=total_seconds
        )
        self.timer_thread.start()

        # 스레드 종료 대기
        self.timer_thread.join()

    def show_break_dialog(self, break_min):
        """
        휴식 다이얼로그 표시. 모달로 열림.
        """
        dlg = BreakDialog(
            parent=self.main_frame,
            title=DIALOG_BREAK,
            break_minutes=break_min,
            config_controller=self.config
        )

        dlg.ShowModal()
        dlg.Destroy()

        # 휴식 후 상태를 다시 STUDY로 복원
        if self.config.is_running:
            self.config.set_status(AppStatus.STUDY)

    def on_close(self, event):
        """
        메인 윈도우 닫기 처리
        """
        self.stop_timer()
        self.main_frame.Destroy()