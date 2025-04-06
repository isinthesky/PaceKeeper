"""
PaceKeeper Qt - 메인 윈도우 UI 업데이트
실시간 UI 상태 업데이트 메서드 모음
"""

from PyQt6.QtWidgets import QPushButton
from app.utils.constants import TimerState, SessionType

def update_ui(self):
    """UI 상태 업데이트"""
    # 타이머 상태에 따른 UI 업데이트
    timer_state = self.timer_controller.get_state()
    
    # 일반 모드 버튼 찾기
    normalStartButton = self.findChild(QPushButton, "normalStartButton")
    normalPauseButton = self.findChild(QPushButton, "normalPauseButton")
    
    if timer_state == TimerState.IDLE:
        # 타이머 정지 상태
        self.startButton.setText("START")
        self.startStopAction.setText("시작")
        self.trayStartStopAction.setText("시작")
        
        self.pauseButton.setEnabled(False)
        self.pauseResumeAction.setEnabled(False)
        self.trayPauseResumeAction.setEnabled(False)
        
        # 일반 모드 버튼 상태 업데이트
        if normalStartButton:
            normalStartButton.setText("START")
        if normalPauseButton:
            normalPauseButton.setEnabled(False)
            
        self.statusLabel.setText("준비")
    
    elif timer_state == TimerState.RUNNING:
        # 타이머 실행 상태
        self.startButton.setText("STOP")
        self.startStopAction.setText("중지")
        self.trayStartStopAction.setText("중지")
        
        self.pauseButton.setText("PAUSE")
        self.pauseResumeAction.setText("일시정지")
        self.trayPauseResumeAction.setText("일시정지")
        
        self.pauseButton.setEnabled(True)
        self.pauseResumeAction.setEnabled(True)
        self.trayPauseResumeAction.setEnabled(True)
        
        # 일반 모드 버튼 상태 업데이트
        if normalStartButton:
            normalStartButton.setText("STOP")
        if normalPauseButton:
            normalPauseButton.setEnabled(True)
            normalPauseButton.setText("PAUSE")
        
        session_type = self.timer_controller.get_session_type()
        session_name = "집중" if session_type == SessionType.POMODORO else "휴식"
        self.statusLabel.setText(f"{session_name} 중...")
    
    elif timer_state == TimerState.PAUSED:
        # 타이머 일시정지 상태
        self.startButton.setText("STOP")
        self.startStopAction.setText("중지")
        self.trayStartStopAction.setText("중지")
        
        self.pauseButton.setText("RESUME")
        self.pauseResumeAction.setText("재개")
        self.trayPauseResumeAction.setText("재개")
        
        self.pauseButton.setEnabled(True)
        self.pauseResumeAction.setEnabled(True)
        self.trayPauseResumeAction.setEnabled(True)
        
        # 일반 모드 버튼 상태 업데이트
        if normalStartButton:
            normalStartButton.setText("STOP")
        if normalPauseButton:
            normalPauseButton.setEnabled(True)
            normalPauseButton.setText("RESUME")
        
        self.statusLabel.setText("일시정지됨")
    
    elif timer_state == TimerState.FINISHED:
        # 타이머 종료 상태
        self.startStopAction.setText("시작")
        self.trayStartStopAction.setText("시작")
        self.pauseResumeAction.setEnabled(False)
        self.trayPauseResumeAction.setEnabled(False)
        
        # 일반 모드 버튼 상태 업데이트
        if normalStartButton:
            normalStartButton.setText("START")
        if normalPauseButton:
            normalPauseButton.setEnabled(False)
            
        self.statusLabel.setText("세션 종료")
    
    # 최근 로그 업데이트
    update_recent_logs(self)
    
    # 태그 목록 업데이트
    update_tags(self)


def update_recent_logs(self):
    """최근 로그 목록 업데이트"""
    # 로그 위젯 초기화
    self.logListWidget.clear()
    
    # 최근 로그 가져오기
    logs = self.main_controller.get_recent_logs()
    
    # 로그 위젯에 추가
    for log in logs:
        self.logListWidget.addLogItem(log.message, log.tags)


def update_tags(self):
    """태그 목록 업데이트"""
    # 태그 위젯 초기화
    self.tagButtonsWidget.clear()
    
    # 태그 목록 가져오기
    tags = self.main_controller.get_all_tags()
    
    # 태그 위젯에 추가
    for tag in tags:
        self.tagButtonsWidget.addTag(tag.name, tag.color)
