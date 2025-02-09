import time
import wx
from pacekeeper.views.break_dialog import BreakDialog
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.sound_manager import SoundManager
from pacekeeper.controllers.timer_controller import TimerController
from pacekeeper.controllers.timer_thread import TimerThread
from pacekeeper.consts.settings import SET_MAIN_DLG_WIDTH, SET_MAIN_DLG_HEIGHT
from pacekeeper.consts.labels import load_language_resource
from pacekeeper.utils import resource_path

lang_res = load_language_resource()

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
        self.sound_manager = SoundManager(self.config)
        self.timer_ctrl = TimerController(self.config)

        # 사운드 파일 정의
        self.long_break_sound = resource_path("assets/sounds/long_brk.wav")
        self.short_break_sound = resource_path("assets/sounds/short_brk.wav")

        # 초기값
        self.timer_thread = None
        self.paused = False
        
    def load_main_size(self):
        self.main_frame.SetSize(self.config.get_setting(SET_MAIN_DLG_WIDTH, 800), 
                               self.config.get_setting(SET_MAIN_DLG_HEIGHT, 300))
                
    def start_timer(self):
        """
        타이머 시작 (공부 시간 -> 휴식 -> 반복)
        """
        study_time_min = self.config.get_setting("study_time", 25)
        total_seconds = study_time_min * 60

        def update_label(time_str):
            wx.CallAfter(self.main_frame.timer_label.SetLabel, time_str)

        def on_finish():
            """공부 타이머가 끝났을 때 호출"""
            if self.config.is_running:
                self.start_break()
        
        self.timer_ctrl.start_timer(
            total_seconds=total_seconds,
            update_callback=update_label,
            on_finish=on_finish,
            pauseable=True,
            app_status_when_running=AppStatus.STUDY
        )

    def stop_timer(self):
        """
        타이머 중지
        """
        self.timer_ctrl.stop_timer()

        
    def toggle_pause(self, event):
        """일시정지/재개 토글 기능"""
        if not self.timer_ctrl.current_thread:
            return

        if self.timer_ctrl.paused:
            self.timer_ctrl.resume_timer()
        else:
            self.timer_ctrl.pause_timer()


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
            
            # 추가된 부분: 타이머 스레드가 완료될 때까지 대기
            while self.timer_thread and self.timer_thread.is_alive():
                time.sleep(0.5)

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
                
    def start_break(self):
        """학습 타이머가 끝난 후 휴식 로직"""
        cycle = self.config.get_cycle()
        
        if cycle % self.config.get_setting("cycles", 4) == 0:
            # 긴 휴식
            break_min = self.config.get_setting("long_break", 15)
            self.config.set_status(AppStatus.LONG_BREAK)
            self.sound_manager.play_sound(self.long_break_sound)
        else:
            # 짧은 휴식
            break_min = self.config.get_setting("short_break", 5)
            self.config.set_status(AppStatus.SHORT_BREAK)
            self.sound_manager.play_sound(self.short_break_sound)

        wx.CallAfter(self.show_break_dialog, break_min)


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
        

    def show_break_dialog(self, break_min):
        """
        휴식 다이얼로그 표시. 모달로 열림.
        """
        dlg = BreakDialog(
            parent=self.main_frame,
            title=lang_res.base_labels['BREAK_DIALOG_TITLE'],
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