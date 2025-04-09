"""
PaceKeeper Qt - 타이머 컨트롤러
타이머 제어 로직 구현 및 시간 관리
"""

from datetime import datetime, timedelta
from typing import Callable, Optional

from PyQt6.QtCore import QDateTime, QObject, QTimer, pyqtSignal

from app.utils.constants import SessionType, TimerState


class TimerController(QObject):
    """타이머 컨트롤러 클래스"""

    # 시그널 정의
    # timerUpdated 시그널은 timerStateChanged로 통합
    timerTick = pyqtSignal(int)  # 남은 시간 (초)
    timerStateChanged = pyqtSignal(TimerState, str)  # 타이머 상태와 포맷된 시간 문자열
    sessionFinished = pyqtSignal(SessionType)  # 세션 타입

    def __init__(self):
        """타이머 컨트롤러 초기화"""
        super().__init__()

        # 상태 변수
        self.totalSeconds = 0
        self.remainingSeconds = 0
        self.startTime = None
        self.pauseTime = None
        self.state = TimerState.IDLE
        self.sessionType = SessionType.POMODORO

        # QTimer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.setInterval(1000)  # 1초마다 업데이트

    def start(
        self, minutes: int = 25, session_type: SessionType = SessionType.POMODORO
    ):
        """
        타이머 시작

        Args:
            minutes: 분 단위 시간
            session_type: 세션 타입
        """
        self.totalSeconds = minutes * 10
        self.remainingSeconds = self.totalSeconds
        self.startTime = datetime.now()
        self.pauseTime = None
        self.sessionType = session_type

        # 상태 변경 및 타이머 시작
        self._set_state(TimerState.RUNNING)
        self.timer.start()

    def pause(self):
        """타이머 일시정지"""
        if self.state == TimerState.RUNNING:
            self.timer.stop()
            self.pauseTime = datetime.now()
            self._set_state(TimerState.PAUSED)

    def resume(self):
        """타이머 재개"""
        if self.state == TimerState.PAUSED:
            # 일시정지 기간 계산 및 보정
            if self.pauseTime:
                pause_duration = (datetime.now() - self.pauseTime).total_seconds()
                self.startTime = self.startTime + timedelta(seconds=pause_duration)

            self.pauseTime = None
            self._set_state(TimerState.RUNNING)
            self.timer.start()

    def stop(self):
        """타이머 중지"""
        self.timer.stop()
        self.remainingSeconds = 0  # 상태 설정 전에 남은 시간 0으로
        self.startTime = None
        self.pauseTime = None
        self._set_state(TimerState.IDLE)

    def get_remaining_time(self) -> int:
        """
        남은 시간 조회 (초 단위)

        Returns:
            남은 시간 (초)
        """
        return self.remainingSeconds

    def get_elapsed_time(self) -> int:
        """
        경과 시간 조회 (초 단위)

        Returns:
            경과 시간 (초)
        """
        return self.totalSeconds - self.remainingSeconds

    def get_progress(self) -> float:
        """
        진행률 조회 (0.0 ~ 1.0)

        Returns:
            진행률 (0.0 ~ 1.0)
        """
        if self.totalSeconds == 0:
            return 0.0
        return (self.totalSeconds - self.remainingSeconds) / self.totalSeconds

    def get_state(self) -> TimerState:
        """
        타이머 상태 조회

        Returns:
            타이머 상태
        """
        return self.state

    def get_session_type(self) -> SessionType:
        """
        세션 타입 조회

        Returns:
            세션 타입
        """
        return self.sessionType

    def is_running(self) -> bool:
        """
        타이머가 실행 중인지 확인

        Returns:
            실행 중 여부
        """
        return self.state == TimerState.RUNNING

    def is_paused(self) -> bool:
        """
        타이머가 일시정지 상태인지 확인

        Returns:
            일시정지 상태 여부
        """
        return self.state == TimerState.PAUSED

    def _update_timer(self):
        """타이머 업데이트 (QTimer에 의해 호출)"""
        # 시스템 시간 기반으로 정확한 시간 계산
        if self.startTime:
            elapsed = int((datetime.now() - self.startTime).total_seconds())
            self.remainingSeconds = max(0, self.totalSeconds - elapsed)
        else:
            # startTime이 없으면 매 초마다 감소
            self.remainingSeconds = max(0, self.remainingSeconds - 1)

        # 시간 표시 업데이트
        self._update_display()

        # 타이머 완료 확인
        if self.remainingSeconds <= 0:
            self.timer.stop()
            self._set_state(TimerState.FINISHED)
            self.sessionFinished.emit(self.sessionType)

    def _update_display(self):
        """타이머 표시 업데이트 (시간만 업데이트 시)"""
        time_str = self._get_formatted_time_str(self.remainingSeconds)

        # 시그널 발생 (상태는 그대로, 시간만 업데이트)
        self.timerStateChanged.emit(self.state, time_str)
        self.timerTick.emit(self.remainingSeconds)

    def _set_state(self, state: TimerState):
        """
        타이머 상태 설정 및 시그널 발생

        Args:
            state: 새 타이머 상태
        """
        if self.state != state:
            self.state = state
            # 상태 변경 시에도 현재 시간 문자열과 함께 시그널 발생
            time_str = self._get_formatted_time_str(self.remainingSeconds)
            self.timerStateChanged.emit(state, time_str)

    def _get_formatted_time_str(self, total_seconds: int) -> str:
        """초를 MM:SS 형식 문자열로 변환"""
        total_seconds = max(0, total_seconds)  # 음수 방지
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
