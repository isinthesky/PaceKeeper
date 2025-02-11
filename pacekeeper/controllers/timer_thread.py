import threading
import time
import wx  # wx 모듈 추가
from typing import Callable, Optional

class TimerThread(threading.Thread):
    """
    TimerThread: 별도 스레드에서 카운트다운을 진행하는 클래스
    - update_callback: 남은 시간을 업데이트하는 콜백 함수 (문자열 인자)
    - on_finish: 타이머 종료 시 호출되는 콜백 함수
    - pauseable: 일시정지 기능 사용 여부
    """
    def __init__(
        self,
        config_controller,
        update_callback: Callable[[str], None],
        total_seconds: int,
        on_finish: Optional[Callable[[], None]] = None,
        pauseable: bool = True
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
                # 일시정지 상태면 재개 신호 대기
                while self.paused and self.pauseable and self._running:
                    self.pause_cond.wait(timeout=1)
            # 남은 시간 계산
            mins, secs = divmod(remaining, 60)
            # 메인 스레드에서 UI 업데이트를 안전하게 수행
            try:
                wx.CallAfter(self.update_callback, f"{mins:02d}:{secs:02d}")
            except Exception as e:
                print("update_callback 호출 에러:", e)
            time.sleep(1)
            remaining -= 1

        # 타이머가 정상 종료된 경우에만 on_finish 호출
        if self._running and self.on_finish:
            self.on_finish()

    def stop(self):
        """타이머 종료 및 스레드 안전 종료 처리"""
        self._running = False
        with self.pause_cond:
            self.pause_cond.notify_all()

    def pause(self):
        """타이머 일시정지"""
        if self.pauseable:
            with self.pause_cond:
                self.paused = True

    def resume(self):
        """타이머 재개"""
        if self.pauseable:
            with self.pause_cond:
                self.paused = False
                self.pause_cond.notify_all()