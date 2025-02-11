# services/timer_service.py
from typing import Callable, Optional
from pacekeeper.controllers.config_controller import ConfigController, AppStatus
from pacekeeper.controllers.timer_thread import TimerThread

class TimerService:
    """
    TimerService: 타이머 기능(시작, 일시정지, 재개, 종료)을 제공하는 서비스 계층
    - ConfigController를 통해 앱 상태 및 설정을 관리
    - update_callback: 남은 시간을 UI에 업데이트하는 콜백 함수
    - on_finish: 타이머 종료 시 호출되는 콜백 함수
    """
    def __init__(
        self,
        config_ctrl: ConfigController,
        update_callback: Callable[[str], None],
        on_finish: Optional[Callable[[], None]] = None,
        pauseable: bool = True
    ):
        self.config_ctrl = config_ctrl
        self.update_callback = update_callback
        self.on_finish = on_finish
        self.pauseable = pauseable
        self.timer_thread: Optional[TimerThread] = None

    def start(self, total_seconds: int):
        """타이머 시작. 기존 타이머가 있으면 먼저 중지."""
        self.stop()  # 이전 타이머 중지

        # 앱 상태 업데이트
        self.config_ctrl.set_status(AppStatus.STUDY)
        self.config_ctrl.is_running = True

        # 타이머 종료 시 호출할 내부 콜백 정의
        def finish_callback():
            if self.config_ctrl.is_running and self.on_finish:
                self.on_finish()

        # TimerThread 생성 및 시작
        self.timer_thread = TimerThread(
            config_controller=self.config_ctrl,
            update_callback=self.update_callback,
            total_seconds=total_seconds,
            on_finish=finish_callback,
            pauseable=self.pauseable
        )
        self.timer_thread.start()

    def stop(self):
        """타이머 중지 및 앱 상태 초기화."""
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.stop()
            self.timer_thread.join(timeout=2)
        self.timer_thread = None
        self.config_ctrl.is_running = False
        self.config_ctrl.set_status(AppStatus.WAIT)

    def pause(self):
        """타이머 일시정지."""
        if self.timer_thread and self.timer_thread.is_alive() and self.pauseable:
            self.timer_thread.pause()

    def resume(self):
        """타이머 재개."""
        if self.timer_thread and self.timer_thread.is_alive() and self.pauseable:
            self.timer_thread.resume()

    def is_paused(self) -> bool:
        """타이머 일시정지 상태 여부 확인."""
        if self.timer_thread:
            return self.timer_thread.paused
        return False

    def is_running(self) -> bool:
        """타이머가 실행 중인지 여부 확인."""
        if self.timer_thread:
            return self.timer_thread.is_alive()
        return False