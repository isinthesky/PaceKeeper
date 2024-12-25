import threading
import time
import wx

class TimerThread(threading.Thread):
    """메인 '작업 시간' 카운트다운을 담당하는 쓰레드"""
    
    def __init__(self, config_controller, main_frame, total_seconds):
        super().__init__()
        self.config = config_controller
        self.main_frame = main_frame
        self.total_seconds = total_seconds
        self._running = True

    def run(self):
        for remaining in range(self.total_seconds, -1, -1):
            if not self.config.is_running or not self._running:
                break

            mins, secs = divmod(remaining, 60)
            time_label = f"{mins:02d}:{secs:02d}"

            try:
                wx.CallAfter(self.main_frame.timer_label.SetLabel, time_label)
            except Exception:
                break

            time.sleep(1)

    def stop(self):
        self._running = False 