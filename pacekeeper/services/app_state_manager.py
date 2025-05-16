# services/app_state_manager.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Callable, Dict, Any, Optional

from pacekeeper.consts.labels import load_language_resource

lang_res = load_language_resource()

@dataclass
class StatusInfo:
    """상태 정보를 담는 데이터 클래스"""
    label: str
    value: int


class AppStatus(Enum):
    """
    애플리케이션 상태를 나타내는 열거형
    
    각 상태는 표시 레이블과 정수 값을 포함한 StatusInfo 객체를 가집니다.
    """
    WAIT = StatusInfo(label=lang_res.base_labels['WAIT'], value=0)
    STUDY = StatusInfo(label=lang_res.base_labels['STUDY'], value=1)
    SHORT_BREAK = StatusInfo(label=lang_res.base_labels['SHORT_BREAK'], value=2)
    LONG_BREAK = StatusInfo(label=lang_res.base_labels['LONG_BREAK'], value=3)
    PAUSED = StatusInfo(label=lang_res.base_labels['PAUSED'], value=4)

    @property
    def label(self) -> str:
        """상태의 레이블 반환"""
        return self.value.label

    @property
    def value_int(self) -> int:
        """상태의 정수 값 반환"""
        return self.value.value

    @classmethod
    def is_break(cls, status: 'AppStatus') -> bool:
        """지정된 상태가 휴식 상태인지 확인"""
        return status in [cls.SHORT_BREAK, cls.LONG_BREAK]


class Observer:
    """상태 변경을 관찰하는 옵저버 인터페이스"""
    def update(self, event_type: str, **kwargs: Any) -> None:
        """
        상태 변경 알림을 받는 메서드
        
        Args:
            event_type: 이벤트 타입 (예: "status_changed", "cycle_changed")
            **kwargs: 이벤트 관련 추가 정보
        """
        pass


class AppStateManager:
    """
    애플리케이션 상태 관리 클래스
    
    상태(AppStatus)와 사이클 카운트를 관리하고, 상태 변경 시 등록된 옵저버에게 알림을 보냅니다.
    """
    def __init__(self) -> None:
        """AppStateManager 초기화"""
        self._status: AppStatus = AppStatus.WAIT
        self._is_running: bool = False
        self._current_cycle: int = 1
        self._observers: List[Observer] = []
    
    def add_observer(self, observer: Observer) -> None:
        """
        상태 변경을 관찰할 옵저버 추가
        
        Args:
            observer: 상태 변경을 관찰할 Observer 인스턴스
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """
        등록된 옵저버 제거
        
        Args:
            observer: 제거할 Observer 인스턴스
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event_type: str, **kwargs: Any) -> None:
        """
        등록된 모든 옵저버에게 알림
        
        Args:
            event_type: 이벤트 타입
            **kwargs: 이벤트 관련 추가 정보
        """
        for observer in self._observers:
            observer.update(event_type, **kwargs)
    
    def get_status(self) -> AppStatus:
        """현재 애플리케이션 상태 반환"""
        return self._status
    
    def set_status(self, status: AppStatus) -> None:
        """
        애플리케이션 상태 설정 및 옵저버에 알림
        
        Args:
            status: 새 애플리케이션 상태
        """
        old_status = self._status
        self._status = status
        self._notify_observers("status_changed", old=old_status, new=status)
    
    def is_running(self) -> bool:
        """애플리케이션 실행 상태 반환"""
        return self._is_running
    
    def set_running(self, running: bool) -> None:
        """
        애플리케이션 실행 상태 설정
        
        Args:
            running: 새 실행 상태
        """
        old_running = self._is_running
        self._is_running = running
        self._notify_observers("running_changed", old=old_running, new=running)
    
    def get_cycle(self) -> int:
        """현재 사이클 수 반환"""
        return self._current_cycle
    
    def set_cycle(self, cycle: int) -> None:
        """
        사이클 수 직접 설정
        
        Args:
            cycle: 새 사이클 수
        """
        old_cycle = self._current_cycle
        self._current_cycle = cycle
        self._notify_observers("cycle_changed", old=old_cycle, new=cycle)
    
    def increment_cycle(self) -> int:
        """
        사이클 수 증가 및 옵저버에 알림
        
        Returns:
            증가된 사이클 수
        """
        old_cycle = self._current_cycle
        self._current_cycle += 1
        self._notify_observers("cycle_changed", old=old_cycle, new=self._current_cycle)
        return self._current_cycle
    
    def start_app(self) -> None:
        """애플리케이션 시작 및 상태 변경"""
        self.set_running(True)
        self.set_status(AppStatus.STUDY)
    
    def stop_app(self) -> None:
        """애플리케이션 중지 및 상태 초기화"""
        self.set_running(False)
        self.set_status(AppStatus.WAIT)
        self.set_cycle(1)