# 이 파일은 더 이상 사용되지 않습니다.
# PyQt5 변환 과정에서 timer_controller.py의 QTimer로 대체되었습니다.
# 참조용으로 보관합니다.

import threading
import time
from collections.abc import Callable

# wx 모듈은 PyQt5로 변환되었으므로 더 이상 필요하지 않습니다.
# import wx


class TimerThread(threading.Thread):
    """
    TimerThread: 별도 스레드에서 카운트다운을 진행하는 클래스
    - update_callback: 남은 시간을 업데이트하는 콜백 함수 (문자열 인자)
    - on_finish: 타이머 종료 시 호출되는 콜백 함수
    - pauseable: 일시정지 기능 사용 여부
    
    참고: 이 클래스는 PyQt5 변환 과정에서 QTimer로 대체되었습니다.
    """
    def __init__(
        self,
        config_controller,
        update_callback: Callable[[str], None],
        total_seconds: int,
        on_finish: Callable[[], None] | None = None,
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
                # PyQt5에서는 QTimer.singleShot 또는 signal/slot을 사용합니다.
                # wx.CallAfter(self.update_callback, f"{mins:02d}:{secs:02d}")
                print("update_callback 호출 (더 이상 사용되지 않음):", f"{mins:02d}:{secs:02d}")
            except Exception as e:
                print("update_callback 호출 에러:", e)
            time.sleep(1)
            remaining -= 1

        # 타이머가 정상 종료된 경우, on_finish 콜백 실행을 메인 스레드로 전환
        if self._running and self.on_finish:
            callback = self.on_finish
            self.on_finish = None  # 중복 호출 방지
            # PyQt5에서는 QTimer.singleShot 또는 signal/slot을 사용합니다.
            # wx.CallAfter(callback)
            print("on_finish 콜백 호출 (더 이상 사용되지 않음)")

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
