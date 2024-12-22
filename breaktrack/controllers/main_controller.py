# controllers/main_controller.py
import threading
import time
import wx
import pygame
from breaktrack.controllers.config_controller import ConfigController, AppStatus
from breaktrack.views.break_dialog import BreakDialog
from breaktrack.models.data_model import DataModel  # 필요하다면

class MainController:
    def __init__(self, main_frame, config_controller: ConfigController):
        """
        메인 프레임과 설정 컨트롤러 참조
        """
        self.main_frame = main_frame
        self.config = config_controller
        self.data_model = DataModel()  # 필요하다면

        # pygame 초기화(알람 사운드용)
        pygame.mixer.init()
        self.long_break_sound = "assets/sounds/long_brk.wav"
        self.short_break_sound = "assets/sounds/short_brk.wav"

        # 메인 프레임의 이벤트 바인딩
        self.main_frame.start_button.Bind(wx.EVT_BUTTON, self.on_start_stop)
        self.main_frame.Bind(wx.EVT_CLOSE, self.on_close)

    def on_start_stop(self, event):
        if not self.config.is_running:
            self.start_timer()
        else:
            self.stop_timer()

    def start_timer(self):
        self.config.start_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, False)
        self.main_frame.start_button.SetLabel("중지")

        self.timer_thread = threading.Thread(target=self.run_timer_loop)
        self.timer_thread.start()

    def stop_timer(self):
        self.config.stop_app()
        self.main_frame.menu_bar.Enable(wx.ID_PREFERENCES, True)
        self.main_frame.start_button.SetLabel("시작")
        if hasattr(self, 'timer_thread') and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=2)

        wx.CallAfter(self.main_frame.timer_label.SetLabel, "00:00")

    def run_timer_loop(self):
        """
        - 작업 시간 -> 휴식 -> 작업 시간 -> 휴식 ... 반복
        - 휴식 시간 카운트다운은 BreakDialog에서 처리
        """
        while self.config.is_running:
            # 사이클 증가
            self.config.increment_cycle()

            study_time = self.config.get_setting("study_time", 25)
            self.countdown(study_time * 60)

            if not self.config.is_running:
                break
            
            # 알람
            # 짧은 휴식 or 긴 휴식
            if self.config.get_cycle() % self.config.get_setting("cycles", 4) == 0:
                self.play_sound(self.long_break_sound)
                break_min = self.config.get_setting("long_break", 15)
                self.config.set_status(AppStatus.LONG_BREAK)
            else:
                self.play_sound(self.short_break_sound)
                break_min = self.config.get_setting("short_break", 5)
                self.config.set_status(AppStatus.SHORT_BREAK)

            # 휴식 다이얼로그 표시 (모달)
            wx.CallAfter(self.show_break_dialog, break_min)

            # break_dialog가 닫힐 때까지 메인 쓰레드에서 잠시 대기
            while self.config.is_running and self.config.get_status() in [AppStatus.SHORT_BREAK, AppStatus.LONG_BREAK]:
                time.sleep(1)

    def countdown(self, total_seconds):
        """작업시간 카운트다운 -> 라벨 갱신"""
        for remaining in range(total_seconds, -1, -1):
            if not self.config.is_running:
                break
            mins, secs = divmod(remaining, 60)
            if self.main_frame:
                try:
                    wx.CallAfter(self.main_frame.timer_label.SetLabel, f"{mins:02d}:{secs:02d}")
                except:
                    break  # 오류 발생시 루프 종료
            time.sleep(1)

    def show_break_dialog(self, break_min):
        dlg = BreakDialog(
            parent=self.main_frame, 
            title="휴식시간",
            break_minutes=break_min,
            config_controller=self.config
        )
        dlg.ShowModal()
        dlg.Destroy()
        # 휴식이 끝났으면 상태를 STUDY로 돌리거나, stop_app() 등 처리
        if self.config.is_running:
            self.config.set_status(AppStatus.STUDY)

    def play_sound(self, sound_file):
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            wx.LogError(f"알람 재생 에러: {e}")

    def on_close(self, event):
        """메인 윈도우 닫기 처리"""
        self.stop_timer()
        self.main_frame.Destroy()