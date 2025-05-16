# controllers/timer_controller.py

from typing import Callable, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from pacekeeper.services.app_state_manager import AppStatus
from pacekeeper.controllers.config_controller import ConfigController

class TimerService(QObject):
    """
    타이머 서비스 클래스
    
    애플리케이션의 타이머 기능(시작, 일시정지, 재개, 종료)을 제공합니다.
    PyQt5의 QTimer를 사용하여 GUI 스레드에서 안전하게 타이머를 실행합니다.
    
    Attributes:
        timer_finished: 타이머 완료 시 발생하는 시그널
    """
    
    # 시그널 정의
    timer_finished = pyqtSignal()
    
    def __init__(
        self,
        config_ctrl: ConfigController,
        update_callback: Callable[[str], None],
        on_finish: Optional[Callable[[], None]] = None,
        pauseable: bool = True
    ) -> None:
        """
        TimerService 초기화
        
        Args:
            config_ctrl: 설정 컨트롤러 인스턴스
            update_callback: 남은 시간을 UI에 업데이트하는 콜백 함수
            on_finish: 타이머 종료 시 호출되는 콜백 함수 (선택적)
            pauseable: 타이머 일시정지 가능 여부 (기본값: True)
        """
        super().__init__()
        
        self.config_ctrl = config_ctrl
        self.update_callback = update_callback
        self.on_finish = on_finish
        self.pauseable = pauseable
        
        # QTimer 초기화
        self.timer = QTimer()
        self.timer.timeout.connect(self._timer_tick)
        
        # 타이머 상태 변수
        self.remaining_seconds: int = 0
        self.paused: bool = False
        self._is_running: bool = False

    def start(self, total_seconds: int) -> None:
        """
        타이머 시작
        
        기존에 실행 중인 타이머가 있으면 먼저 중지하고 새 타이머를 시작합니다.
        
        Args:
            total_seconds: 타이머 실행 시간 (초)
        """
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

    def stop(self) -> None:
        """
        타이머 중지 및 앱 상태 초기화
        
        실행 중인 타이머를 중지하고 모든 상태를 초기화합니다.
        """
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

    def pause(self) -> None:
        """
        타이머 일시정지
        
        타이머가 실행 중이고 일시정지 가능한 경우에만 일시정지합니다.
        """
        if self._is_running and self.pauseable and not self.paused:
            self.timer.stop()
            self.paused = True
            self.config_ctrl.set_status(AppStatus.PAUSED)

    def resume(self) -> None:
        """
        타이머 재개
        
        타이머가 일시정지 상태이고 일시정지 가능한 경우에만 재개합니다.
        """
        if self._is_running and self.pauseable and self.paused:
            self.paused = False
            self.timer.start(1000)
            
            # 이전 상태로 복원 (학습 또는 휴식)
            current_status = self.config_ctrl.get_status()
            if current_status == AppStatus.PAUSED:
                self.config_ctrl.set_status(AppStatus.STUDY)  # 기본값으로 학습 상태 설정

    def is_paused(self) -> bool:
        """
        타이머 일시정지 상태 여부 확인
        
        Returns:
            타이머가 일시정지 상태이면 True, 아니면 False
        """
        return self.paused

    def is_running(self) -> bool:
        """
        타이머 실행 중 여부 확인
        
        Returns:
            타이머가 실행 중이면 True, 아니면 False
        """
        return self._is_running
    
    def get_remaining_time(self) -> tuple[int, int]:
        """
        현재 남은 시간을 분:초 형식으로 반환
        
        Returns:
            (분, 초) 튜플
        """
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return (minutes, seconds)
    
    def _timer_tick(self) -> None:
        """
        타이머 틱 처리 - 1초마다 호출됨
        
        남은 시간을 감소시키고 UI를 업데이트합니다.
        타이머가 종료되면 완료 시그널을 발생시킵니다.
        """
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
        else:
            self.timer.stop()
            self._is_running = False
            self.timer_finished.emit()
    
    def _update_display(self) -> None:
        """
        남은 시간을 UI에 표시
        
        현재 남은 시간을 MM:SS 형식으로 변환하여 update_callback 함수를 통해 UI에 전달합니다.
        """
        minutes, seconds = self.get_remaining_time()
        time_str = f"{minutes:02}:{seconds:02}"
        
        if self.update_callback:
            self.update_callback(time_str)
    
    def _on_timer_finished(self) -> None:
        """
        타이머 종료 시 호출되는 내부 처리
        
        타이머 종료 시 외부에서 전달받은 on_finish 콜백 함수를 호출합니다.
        """
        if self.on_finish:
            self.on_finish()