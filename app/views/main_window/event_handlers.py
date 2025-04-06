"""
PaceKeeper Qt - 메인 윈도우 이벤트 핸들러
이벤트 및 시그널 처리 메서드 모음
"""

from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCloseEvent
from datetime import datetime

from app.utils.constants import TimerState, SessionType


def connect_signals(self):
    """시그널 연결"""
    # 타이머 위젯 시그널
    self.timerWidget.timerStarted.connect(self.onTimerStart)
    self.timerWidget.timerPaused.connect(self.onTimerPause)
    self.timerWidget.timerStopped.connect(self.onTimerStop)
    
    # 타이머 컨트롤러 시그널
    self.timer_controller.timerUpdated.connect(self.timerWidget.updateTimer)
    self.timer_controller.timerStateChanged.connect(self.onTimerStateChanged)
    self.timer_controller.sessionFinished.connect(self.onSessionFinished)
    
    # 메인 컨트롤러 시그널
    self.main_controller.sessionStarted.connect(self.onSessionStarted)
    self.main_controller.sessionPaused.connect(self.onSessionPaused)
    self.main_controller.sessionResumed.connect(self.onSessionResumed)
    self.main_controller.sessionStopped.connect(self.onSessionStopped)
    self.main_controller.sessionFinished.connect(self.onSessionFinished)
    
    # 텍스트 입력 위젯 시그널
    self.textInputWidget.textSubmitted.connect(self.onTextSubmitted)
    
    # 태그 위젯 시그널
    self.tagButtonsWidget.tagSelected.connect(self.onTagSelected)
    
    # 로그 위젯 시그널
    self.logListWidget.logSelected.connect(self.onLogSelected)


def on_timer_start(self):
    """타이머 시작 이벤트 핸들러"""
    # 현재 입력된 텍스트 가져오기
    current_text = self.textInputWidget.text()
    
    # 텍스트가 있으면 로그 등록
    if current_text and current_text.strip():
        # 현재 시간으로 로그 생성
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 로그 생성
        self.log_service.create_log(
            message=current_text,
            start_date=start_date
        )
        
        # 최근 로그 업데이트
        self.updateRecentLogs()
    
    # 세션 시작
    self.main_controller.start_session()


def on_timer_pause(self):
    """타이머 일시정지 이벤트 핸들러"""
    self.main_controller.toggle_pause()


def on_timer_stop(self):
    """타이머 중지 이벤트 핸들러"""
    self.main_controller.stop_session()


def on_timer_state_changed(self, state):
    """
    타이머 상태 변경 이벤트 핸들러
    
    Args:
        state: 타이머 상태
    """
    self.updateUI()


def on_session_started(self, session_type):
    """
    세션 시작 이벤트 핸들러
    
    Args:
        session_type: 세션 타입
    """
    self.updateUI()


def on_session_paused(self):
    """세션 일시정지 이벤트 핸들러"""
    self.updateUI()


def on_session_resumed(self):
    """세션 재개 이벤트 핸들러"""
    self.updateUI()


def on_session_stopped(self):
    """세션 중지 이벤트 핸들러"""
    self.updateUI()


def on_session_finished(self, session_type):
    """
    세션 완료 이벤트 핸들러
    
    Args:
        session_type: 세션 타입
    """
    self.updateUI()
    
    # 뽀모도로 세션이 완료되면 휴식 대화상자 표시
    if session_type == SessionType.POMODORO:
        # 다음 세션 타입 결정
        next_session_type = SessionType.SHORT_BREAK
        pomodoro_count = self.main_controller.pomodoro_count
        if pomodoro_count % self.config.get("long_break_interval", 4) == 0:
            next_session_type = SessionType.LONG_BREAK
        
        # 휴식 대화상자 표시
        self.showBreakDialog(next_session_type)


def on_text_submitted(self, text):
    """
    텍스트 제출 이벤트 핸들러
    
    Args:
        text: 제출된 텍스트
    """
    # 현재 입력 텍스트 설정
    self.main_controller.set_log_text(text)
    
    # 타이머가 실행 중이 아니면 로그 추가
    timer_state = self.timer_controller.get_state()
    if timer_state != TimerState.RUNNING:
        # 로그 생성 (0분 로그)
        self.log_service.create_log(message=text)
        
        # 최근 로그 업데이트
        self.updateRecentLogs()


def on_tag_selected(self, tag_name):
    """
    태그 선택 이벤트 핸들러
    
    Args:
        tag_name: 선택된 태그 이름
    """
    # 현재 입력 텍스트에 태그 추가
    current_text = self.textInputWidget.text()
    if current_text:
        self.textInputWidget.setPlainText(f"{current_text} #{tag_name}")
    else:
        self.textInputWidget.setPlainText(f"#{tag_name}")


def on_log_selected(self, log_text):
    """
    로그 선택 이벤트 핸들러
    
    Args:
        log_text: 선택된 로그 텍스트
    """
    # 로그 텍스트를 입력 필드에 설정
    self.textInputWidget.setPlainText(log_text)


def on_tray_icon_activated(self, reason):
    """
    트레이 아이콘 활성화 이벤트 핸들러
    
    Args:
        reason: 활성화 이유
    """
    if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
        self.showNormal()


def on_exit_from_tray(self):
    """트레이 메뉴에서 종료 이벤트 핸들러"""
    # 애플리케이션 종료
    QCoreApplication.quit()


def close_event(self, event: QCloseEvent):
    """
    창 닫기 이벤트 처리
    
    Args:
        event: 닫기 이벤트
    """
    if self.config.get("minimize_to_tray", True):
        # 트레이로 최소화
        event.ignore()
        self.hide()
        
        # 트레이 메시지 표시
        self.trayIcon.showMessage(
            "PaceKeeper",
            "PaceKeeper가 트레이로 최소화되었습니다.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    else:
        # 종료 확인
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "종료 확인",
            "PaceKeeper를 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 타이머 중지
            self.main_controller.stop_session()
            
            # 이벤트 수락 (창 닫기)
            event.accept()
        else:
            # 이벤트 무시 (창 닫기 취소)
            event.ignore()
