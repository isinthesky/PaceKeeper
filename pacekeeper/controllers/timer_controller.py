# services/timer_service.py
from typing import Callable, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from pacekeeper.controllers.config_controller import ConfigController, AppStatus

class TimerService(QObject):
    """
    TimerService: 타이머 기능(시작, 일시정지, 재개, 종료)을 제공하는 서비스 계층
    - ConfigController를 통해 앱 상태 및 설정을 관리
    - update_callback: 남은 시간을 UI에 업데이트하는 콜백 함수
    - on_finish: 타이머 종료 시 호출되는 콜백 함수
    
    PyQt5로 변환: wxPython의 TimerThread를 QTimer로 대체하여 GUI 스레드에서 안전하게 타이머 실행
    """
    
    # 시그널 정의
    timer_finished = pyqtSignal()
    
    def __init__(
        self,
        config_ctrl: ConfigController,
        update_callback: Callable[[str], None],
        on_finish: Optional[Callable[[], None]] = None,
        pauseable: bool = True
    ):
        super().__init__()
        
        self.config_ctrl = config_ctrl
        self.update_callback = update_callback
        self.on_finish = on_finish
        self.pauseable = pauseable
        
        # QTimer 초기화
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)
        
        # 타이머 상태 변수
        self.remaining_seconds = 0
        self.paused = False
        self._is_running = False

    def start(self, total_seconds: int):
        """타이머 시작. 기존 타이머가 있으면 먼저 중지."""
        self.stop()  # 이전 타이머 중지

        # 앱 상태 업데이트
        self.config_ctrl.set_status(AppStatus.STUDY)
        self.config_ctrl.is_running = True
        
        # 타이머 종료 시 호출할 내부 콜백 연결
        self.timer_finished.connect(self._on_timer_finished)
        
        # 타이머 초기화 및 시작
        self.remaining_seconds = total_seconds
        self._is_running = True
        self.paused = False
        
        self._update_display()  # 초기 표시 업데이트
        self.timer.start(1000)  # 1초마다 tick

    def stop(self):
        """타이머 중지 및 앱 상태 초기화."""
        if self._is_running:
            self.timer.stop()
            self._is_running = False
            self.paused = False
            self.remaining_seconds = 0
            
            # 시그널 연결 해제
            try:
                self.timer_finished.disconnect()
            except TypeError:
                # 연결된 슬롯이 없는 경우 예외 처리
                pass
                
        self.config_ctrl.is_running = False
        self.config_ctrl.set_status(AppStatus.WAIT)

    def pause(self):
        """타이머 일시정지."""
        if self._is_running and self.pauseable and not self.paused:
            self.timer.stop()
            self.paused = True

    def resume(self):
        """타이머 재개."""
        if self._is_running and self.pauseable and self.paused:
            self.paused = False
            self.timer.start(1000)

    def is_paused(self) -> bool:
        """타이머 일시정지 상태 여부 확인."""
        return self.paused

    def is_running(self) -> bool:
        """타이머가 실행 중인지 여부 확인."""
        return self._is_running
    
    def _timer_tick(self):
        """타이머 틱 처리 - 1초마다 호출됨"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
        else:
            self.timer.stop()
            self._is_running = False
            self.timer_finished.emit()
    
    def _update_display(self):
        """남은 시간을 UI에 표시"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        time_str = f"{minutes:02}:{seconds:02}"
        
        if self.update_callback:
            self.update_callback(time_str)
    
    def _on_timer_finished(self):
        """타이머 종료 시 호출되는 내부 처리"""
        if self.on_finish:
            self.on_finish()