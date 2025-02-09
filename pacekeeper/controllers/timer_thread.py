# breaktrack/controllers/timer_thread.py
import threading
import time
import wx
from .config_controller import AppStatus

class TimerThread(threading.Thread):
    """공용 타이머 스레드"""
    def __init__(
        self,
        config_controller,
        update_callback,
        total_seconds,
        on_finish=None,
        pauseable=True
    ):
        super().__init__()
        self.config = config_controller
        self.update_callback = update_callback
        self.total_seconds = total_seconds
        self.on_finish = on_finish
        self.pauseable = pauseable

        self._running = True
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())

    def run(self):
        remaining = self.total_seconds
        while remaining >= 0 and self._running:
            with self.pause_cond:
                # 일시정지 상태라면 재개 신호 대기
                while self.paused and self.pauseable and self._running:
                    self.pause_cond.wait(timeout=1)
            
            # 남은 시간 표시
            mins, secs = divmod(remaining, 60)
            try:
                self.update_callback(f"{mins:02d}:{secs:02d}")
            except:
                pass  # UI가 닫혔거나 에러 발생 시 무시

            time.sleep(1)
            remaining -= 1

        # 완료 콜백
        if self._running and self.on_finish:
            self.on_finish()

    def stop(self):
        self._running = False
        # 일시정지 상태라면 resume 시켜서 안전 종료
        with self.pause_cond:
            self.pause_cond.notify_all()

    def pause(self):
        if self.pauseable:
            with self.pause_cond:
                self.paused = True

    def resume(self):
        if self.pauseable:
            with self.pause_cond:
                self.paused = False
                self.pause_cond.notify_all()
