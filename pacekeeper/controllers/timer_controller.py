# breaktrack/controllers/timer_controller.py
from typing import Callable, Optional
from .config_controller import ConfigController, AppStatus
from .timer_thread import TimerThread


class TimerController:
    def __init__(self, config_ctrl: ConfigController):
        self.config_ctrl = config_ctrl
        self.current_thread: Optional[TimerThread] = None
        self.paused = False

    def start_timer(
        self,
        total_seconds: int,
        update_callback: Callable[[str], None],
        on_finish: Optional[Callable[[], None]] = None,
        pauseable: bool = True,
        app_status_when_running: AppStatus = AppStatus.STUDY
    ):
        """통합 타이머 시작 함수."""
        # 혹시 이전 타이머가 동작중이면 정지
        self.stop_timer()

        # 앱 상태 설정
        self.config_ctrl.set_status(app_status_when_running)
        self.config_ctrl.is_running = True
        self.paused = False

        # TimerThread 생성
        def finish_callback():
            """타이머 완료 콜백."""
            if on_finish and self.config_ctrl.is_running:
                on_finish()


        self.current_thread = TimerThread(
            config_controller=self.config_ctrl,
            update_callback=update_callback,
            total_seconds=total_seconds,
            on_finish=finish_callback,
            pauseable=pauseable,
        )

        self.current_thread.start()

    def stop_timer(self):
        """타이머 중지."""
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.stop()
            self.current_thread.join(timeout=2)
        self.current_thread = None
        self.paused = False
        self.config_ctrl.is_running = False
        self.config_ctrl.set_status(AppStatus.WAIT)

    def pause_timer(self):
        """타이머 일시정지."""
        if not self.current_thread or not self.current_thread.is_alive():
            return
        if self.paused:
            return  # 이미 일시정지 상태면 무시

        self.current_thread.pause()
        self.paused = True

    def resume_timer(self):
        """타이머 재개."""
        if not self.current_thread or not self.current_thread.is_alive():
            return
        if not self.paused:
            return  # 이미 재개 상태면 무시

        self.current_thread.resume()
        self.paused = False
