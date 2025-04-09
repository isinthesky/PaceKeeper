"""
PaceKeeper Qt - 메인 컨트롤러
애플리케이션 핵심 로직 관리 및 컴포넌트 연결
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from app.config.app_config import AppConfig
from app.controllers.timer_controller import TimerController
from app.domain.log.log_service import LogService
from app.domain.tag.tag_service import TagService
from app.domain.category.category_service import CategoryService
from app.domain.log.log_entity import LogEntity
from app.domain.tag.tag_entity import TagEntity
from app.domain.category.category_entity import CategoryEntity
from app.utils.constants import TimerState, SessionType


class MainController(QObject):
    """애플리케이션 메인 컨트롤러 클래스"""
    
    # 시그널 정의
    sessionStarted = pyqtSignal(SessionType)  # 세션 시작
    sessionPaused = pyqtSignal()  # 세션 일시정지
    sessionResumed = pyqtSignal()  # 세션 재개
    sessionStopped = pyqtSignal()  # 세션 중지
    sessionFinished = pyqtSignal(SessionType)  # 세션 완료
    logCreated = pyqtSignal(LogEntity)  # 로그 생성
    tagsLoaded = pyqtSignal(list)  # 태그 목록 로드
    categoriesLoaded = pyqtSignal(list)  # 카테고리 목록 로드
    
    def __init__(self, app_config: Optional[AppConfig] = None,
                 timer_controller: Optional[TimerController] = None,
                 log_service: Optional[LogService] = None,
                 tag_service: Optional[TagService] = None,
                 category_service: Optional[CategoryService] = None):
        """
        메인 컨트롤러 초기화
        
        Args:
            app_config: 애플리케이션 설정 관리자
            timer_controller: 타이머 컨트롤러
            log_service: 로그 서비스
            tag_service: 태그 서비스
            category_service: 카테고리 서비스
        """
        super().__init__()
        
        # 컴포넌트 초기화
        self.config = app_config or AppConfig()
        self.timer_controller = timer_controller or TimerController()
        self.log_service = log_service or LogService()
        self.tag_service = tag_service or TagService()
        self.category_service = category_service or CategoryService()
        
        # 상태 변수
        self.session_start_time = None
        self.current_session_type = SessionType.POMODORO
        self.pomodoro_count = 0
        self.should_auto_start_break = False
        self.should_auto_start_pomodoro = False
        self.current_category_id = None
        self.current_log_text = ""
        
        # 시그널 연결
        self._connect_signals()
    
    def _connect_signals(self):
        """시그널-슬롯 연결"""
        # 타이머 컨트롤러 시그널 연결
        self.timer_controller.timerStateChanged.connect(self._on_timer_state_changed)
        self.timer_controller.sessionFinished.connect(self._on_session_finished)
        
        # 서비스 시그널 연결
        self.log_service.logCreated.connect(self.logCreated)
        self.tag_service.tagsChanged.connect(self._on_tags_changed)
        self.category_service.categoriesChanged.connect(self._on_categories_changed)
    
    def start_session(self, session_type: Optional[SessionType] = None, 
                     category_id: Optional[int] = None,
                     message: Optional[str] = None):
        """
        세션 시작
        
        Args:
            session_type: 세션 타입 (None이면 기본값 사용)
            category_id: 카테고리 ID
            message: 로그 메시지 (뽀모도로 세션 시작 시 사용)
        """
        # 세션 타입 결정
        if session_type is None:
            if self.timer_controller.get_state() == TimerState.FINISHED:
                # 이전 세션이 완료되었으면 다음 세션 타입 결정
                if self.current_session_type == SessionType.POMODORO:
                    # 뽀모도로 세션 후에는 휴식
                    if self.pomodoro_count % self.config.get("long_break_interval", 4) == 0:
                        session_type = SessionType.LONG_BREAK
                    else:
                        session_type = SessionType.SHORT_BREAK
                else:
                    # 휴식 세션 후에는 뽀모도로
                    session_type = SessionType.POMODORO
            else:
                # 기본은 뽀모도로
                session_type = SessionType.POMODORO
        
        self.current_session_type = session_type
        self.current_category_id = category_id
        self.session_start_time = datetime.now()
        
        # 세션 타입에 따른 시간 설정
        minutes = 0
        if session_type == SessionType.POMODORO:
            minutes = self.config.get("study_time", 25)
            if self.current_session_type == SessionType.POMODORO:
                self.pomodoro_count += 1
            
            # 뽀모도로 세션 시작 시 로그 생성 (message가 있을 경우)
            if message and message.strip():
                start_date_str = self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")
                # 로그 생성 (tags는 자동으로 추출되거나 별도 관리 필요)
                # log_service.create_log는 logCreated 시그널을 발생시키므로 직접 호출
                self.log_service.create_log(
                    message=message,
                    start_date=start_date_str
                    # category_id 는 현재 LogEntity에서 관리하지 않음
                    # tags 는 LogService 내부에서 추출하거나, UI에서 전달받는 방식 고려
                )
                # 생성된 로그 정보를 내부 상태에 둘 필요는 없을 수 있음 (UI는 시그널로 업데이트)
                # self.current_log_text = message # 필요 시 주석 해제
        elif session_type == SessionType.SHORT_BREAK:
            minutes = self.config.get("break_time", 5)
        elif session_type == SessionType.LONG_BREAK:
            minutes = self.config.get("long_break_time", 15)
        
        # 타이머 시작
        self.timer_controller.start(minutes, session_type)
        
        # 자동 시작 설정
        self.should_auto_start_break = self.config.get("auto_start_breaks", True)
        self.should_auto_start_pomodoro = self.config.get("auto_start_pomodoros", False)
        
        # 시그널 발생
        self.sessionStarted.emit(session_type)
    
    def pause_session(self):
        """세션 일시정지"""
        if self.timer_controller.is_running():
            self.timer_controller.pause()
            self.sessionPaused.emit()
    
    def resume_session(self):
        """세션 재개"""
        if self.timer_controller.is_paused():
            self.timer_controller.resume()
            self.sessionResumed.emit()
    
    def stop_session(self, save_log: bool = True):
        """
        세션 중지
        
        Args:
            save_log: 로그 저장 여부
        """
        # 현재 상태 확인
        if self.timer_controller.get_state() in [TimerState.IDLE, TimerState.FINISHED]:
            return
        
        # 세션 종료 시간
        end_time = datetime.now()
        
        # 세션 중지
        self.timer_controller.stop()
        
        # 로그 저장 (뽀모도로 세션이었을 경우만)
        if save_log and self.current_session_type == SessionType.POMODORO and self.session_start_time:
            if self.current_log_text:
                duration = int((end_time - self.session_start_time).total_seconds())
                self._save_log(self.current_log_text, duration)
        
        # 세션 상태 초기화
        self.session_start_time = None
        self.current_log_text = ""
        
        # 시그널 발생
        self.sessionStopped.emit()
    
    def toggle_pause(self):
        """세션 일시정지/재개 토글"""
        if self.timer_controller.is_running():
            self.pause_session()
        elif self.timer_controller.is_paused():
            self.resume_session()
    
    def set_log_text(self, text: str):
        """
        로그 텍스트 설정
        
        Args:
            text: 로그 텍스트
        """
        self.current_log_text = text
    
    def get_recent_logs(self, limit: int = 10) -> List[LogEntity]:
        """
        최근 로그 항목 조회
        
        Args:
            limit: 반환할 최대 항목 수
            
        Returns:
            로그 항목 객체 목록
        """
        return self.log_service.get_recent_logs(limit)
    
    def get_all_tags(self) -> List[TagEntity]:
        """
        모든 태그 조회
        
        Returns:
            태그 객체 목록
        """
        return self.tag_service.get_all_tags()
    
    def get_all_categories(self) -> List[CategoryEntity]:
        """
        모든 카테고리 조회
        
        Returns:
            카테고리 객체 목록
        """
        return self.category_service.get_all_categories()
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        통계 정보 조회
        
        Args:
            days: 조회할 일 수
            
        Returns:
            통계 정보
        """
        return self.log_service.get_total_stats(days)
    
    def _on_timer_state_changed(self, state: TimerState):
        """
        타이머 상태 변경 이벤트 핸들러
        
        Args:
            state: 타이머 상태
        """
        pass  # 필요시 추가 로직 구현
    
    def _on_session_finished(self, session_type: SessionType):
        """
        세션 완료 이벤트 핸들러
        
        Args:
            session_type: 세션 타입
        """
        # 뽀모도로 세션 완료 시 로그 저장
        if session_type == SessionType.POMODORO and self.session_start_time:
            end_time = datetime.now()
            duration = int((end_time - self.session_start_time).total_seconds())
            
            if self.current_log_text:
                self._save_log(self.current_log_text, duration)
        
        # 자동 시작 설정 확인 및 저장 (실제 시작은 BreakDialog에서 처리)
        if session_type == SessionType.POMODORO:
            # 뽀모도로 세션 후에는 휴식
            self.should_auto_start_break = self.config.get("auto_start_breaks", True)
        else:
            # 휴식 세션 후에는 뽀모도로
            self.should_auto_start_pomodoro = self.config.get("auto_start_pomodoros", False)
        
        # 참고: 다음 세션 자동 시작 코드 제거함 - BreakDialog가 표시되고 나서 시작되도록 함
        
        # 시그널 발생
        self.sessionFinished.emit(session_type)
    
    def _on_tags_changed(self):
        """태그 목록 변경 이벤트 핸들러"""
        tags = self.tag_service.get_all_tags()
        self.tagsLoaded.emit(tags)
    
    def _on_categories_changed(self):
        """카테고리 목록 변경 이벤트 핸들러"""
        categories = self.category_service.get_all_categories()
        self.categoriesLoaded.emit(categories)
    
    def _save_log(self, message: str, duration: int):
        """
        로그 저장
        
        Args:
            message: 로그 메시지
            duration: 지속 시간 (초)
        """
        if not message or not message.strip() or not self.session_start_time:
            return
        
        # 로그 생성 (LogService.create_log 사용)
        # duration 정보는 현재 LogEntity에 저장되지 않음
        start_date_str = self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # tags는 LogService 내부에서 추출하거나 None 전달
            self.log_service.create_log(
                message=message,
                start_date=start_date_str,
                # category_id 는 현재 LogEntity에서 관리하지 않음
                # end_date는 필요 시 계산하여 전달
            )
            
            # 로그 생성 성공 후 내부 상태 초기화?
            self.current_log_text = "" # 여기서는 초기화하지 않고 호출하는 쪽에서 관리
            
        except ValueError as e:
            # 로그 생성 실패 처리 (예: 로깅)
            print(f"로그 저장 실패: {e}")
